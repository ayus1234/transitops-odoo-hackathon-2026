"""
Vehicle Telemetry & WebSocket API Router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import UUID4
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User
from app.schemas.telemetry import (
    TelemetryIngestBatchRequest,
    TelemetryIngestResponse,
    TelemetryLogResponse,
    FleetLiveLocationResponse,
)
from app.services.telemetry_service import TelemetryService
from app.core.websocket_manager import ws_manager
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/telemetry", tags=["Connected Fleet Telemetry (IoT)"])


@router.post("/ingest", response_model=TelemetryIngestResponse)
async def ingest_telemetry_batch(
    request: TelemetryIngestBatchRequest,
    db: Session = Depends(get_db)
):
    """High-throughput IoT GPS & OBD-II telemetry ingestion endpoint."""
    service = TelemetryService(db)
    response = service.ingest_telemetry_batch(request)
    
    # Broadcast live updates via WebSocket to connected dispatcher dashboards
    live_positions = service.get_live_fleet_positions()
    await ws_manager.broadcast({
        "type": "FLEET_LOCATION_UPDATE",
        "timestamp": str(response.timestamps_range.get("processed_at")),
        "vehicles": [p.model_dump() for p in live_positions]
    })
    
    return response


@router.get("/live", response_model=List[FleetLiveLocationResponse])
def get_live_fleet_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """Get current live GPS locations, speeds, and online/offline heartbeat state for all fleet vehicles."""
    service = TelemetryService(db)
    return service.get_live_fleet_positions()


@router.get("/vehicles/{vehicle_id}/breadcrumbs", response_model=List[TelemetryLogResponse])
def get_vehicle_breadcrumbs(
    vehicle_id: UUID4,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """Get historical GPS breadcrumb logs for route playback."""
    service = TelemetryService(db)
    return service.get_vehicle_breadcrumbs(vehicle_id=vehicle_id, limit=limit)


@router.websocket("/ws/live")
async def fleet_live_websocket(websocket: WebSocket):
    """Real-time WebSocket endpoint for Dispatcher Control Tower live map updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open & receive any client pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
