"""
Routing & Multi-Stop ETA Control Center API Router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import UUID4
from typing import Optional

from app.core.database import get_db
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User
from app.schemas.routing import (
    RouteCalculationRequest,
    RouteCalculationResponse,
    MultiStopETAResponse
)
from app.services.routing.routing_service import RoutingService
from app.utils.exceptions import NotFoundError, BusinessLogicError

router = APIRouter(prefix="/routing", tags=["Routing & Multi-Stop ETA"])


@router.post("/calculate", response_model=RouteCalculationResponse)
def calculate_route(
    request: RouteCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Calculate route distance, duration, leg details, and geometry polyline."""
    service = RoutingService(db)
    return service.calculate_route(request)


@router.post("/trips/{trip_id}/calculate-eta", response_model=MultiStopETAResponse)
def calculate_trip_eta(
    trip_id: UUID4,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """Calculate and update stop-by-stop ETAs, planned arrivals, and route geometry for a trip."""
    service = RoutingService(db)
    try:
        return service.calculate_multi_stop_eta(trip_id=trip_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
