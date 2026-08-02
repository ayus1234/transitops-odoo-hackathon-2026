"""
Dispatch Control Center API Router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, UUID4

from app.core.database import get_db
from app.services.dispatch_service import DispatchService
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User
from app.schemas.trip import TripResponse

router = APIRouter(prefix="/dispatch", tags=["Dispatch & Control Tower"])


class DispatchRequest(BaseModel):
    job_id: UUID4
    vehicle_id: UUID4
    driver_id: UUID4
    notes: Optional[str] = None


@router.get("/board")
def get_dispatch_board(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get operational dispatch board queues, assets, and live KPIs."""
    service = DispatchService(db)
    return service.get_dispatch_board_data()


@router.post("/validate")
def validate_dispatch(
    request: DispatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Dry-run validation checks before dispatching."""
    service = DispatchService(db)
    return service.validate_dispatch(
        job_id=request.job_id,
        vehicle_id=request.vehicle_id,
        driver_id=request.driver_id
    )


@router.post("/assign-and-dispatch", response_model=TripResponse)
def assign_and_dispatch(
    request: DispatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """Assign vehicle and driver to customer job and operational dispatch."""
    service = DispatchService(db)
    trip = service.assign_and_dispatch(
        job_id=request.job_id,
        vehicle_id=request.vehicle_id,
        driver_id=request.driver_id,
        notes=request.notes
    )
    return TripResponse.model_validate(trip)
