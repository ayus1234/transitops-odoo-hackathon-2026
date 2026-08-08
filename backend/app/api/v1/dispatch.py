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
from app.utils.exceptions import BusinessLogicError

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
    try:
        trip = service.assign_and_dispatch(
            job_id=request.job_id,
            vehicle_id=request.vehicle_id,
            driver_id=request.driver_id,
            notes=request.notes
        )
        return TripResponse.model_validate(trip)
    except BusinessLogicError as e:
        if e.code == "BIZ_DISPATCH_CONFLICT":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


from app.services.vehicle_recommendation_service import VehicleRecommendationService
from app.schemas.vehicle_recommendation import VehicleRecommendationResponse

@router.get("/recommendations/{job_id}", response_model=VehicleRecommendationResponse)
def get_vehicle_recommendations(
    job_id: UUID4,
    top_n: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get multi-factor AI/algorithmic vehicle and driver recommendations for a job."""
    service = VehicleRecommendationService(db)
    return service.recommend_vehicles_for_job(job_id=job_id, top_n=top_n)

