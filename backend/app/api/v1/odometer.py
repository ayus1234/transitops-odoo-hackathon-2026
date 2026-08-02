"""
Odometer API endpoints.
Nested under /vehicles/{vehicle_id}/odometer.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.odometer import (
    OdometerReadingCreate,
    OdometerReadingResponse,
    OdometerStatsResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.services.odometer_service import OdometerService


router = APIRouter()


@router.post(
    "/{vehicle_id}/odometer",
    response_model=OdometerReadingResponse,
    status_code=status.HTTP_201_CREATED
)
def record_odometer_reading(
    vehicle_id: UUID,
    data: OdometerReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "update"))
):
    """
    Record a new odometer reading for a vehicle.

    Permissions: vehicles:update

    Business Rules:
    - Reading must be ≥ previous reading (anti-regression)
    - Source 'correction' overrides anti-regression check
    - Automatically updates Vehicle.current_odometer_km
    """
    service = OdometerService(db)
    reading = service.record_reading(vehicle_id, data, current_user)
    return OdometerReadingResponse.model_validate(reading)


@router.get(
    "/{vehicle_id}/odometer",
    response_model=PaginatedResponse[OdometerReadingResponse]
)
def get_odometer_history(
    vehicle_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """
    Get paginated odometer reading history for a vehicle.

    Permissions: vehicles:read
    """
    service = OdometerService(db)
    readings, total = service.get_history(vehicle_id, page=page, page_size=page_size)

    return PaginatedResponse(
        success=True,
        data=[OdometerReadingResponse.model_validate(r) for r in readings],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.get(
    "/{vehicle_id}/odometer/stats",
    response_model=OdometerStatsResponse
)
def get_odometer_stats(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """
    Get odometer distance and utilisation statistics for a vehicle.

    Permissions: vehicles:read
    """
    service = OdometerService(db)
    stats = service.get_stats(vehicle_id)
    return OdometerStatsResponse(**stats)
