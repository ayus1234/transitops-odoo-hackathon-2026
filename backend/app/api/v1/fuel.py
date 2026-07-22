"""
Fuel API endpoints.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.fuel import (
    FuelCreate,
    FuelUpdate,
    FuelResponse,
    FuelListResponse,
    FuelEfficiencyStats
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.fuel_service import FuelService


router = APIRouter()


# ============================================================
# STATIC ROUTES (must come before /{fuel_id})
# ============================================================

@router.get("/efficiency", response_model=dict)
def get_fuel_efficiency(
    vehicle_id: UUID | None = Query(None, description="Filter by vehicle ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "read"))
):
    """
    Get fuel efficiency statistics.

    Permissions: fuel:read
    """
    service = FuelService(db)
    stats = service.get_efficiency_stats(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date
    )
    return {
        "success": True,
        "data": [FuelEfficiencyStats.model_validate(s) for s in stats]
    }


# ============================================================
# COLLECTION ROUTES
# ============================================================

@router.get("", response_model=PaginatedResponse[FuelListResponse])
def list_fuel_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    vehicle_id: UUID | None = Query(None, description="Filter by vehicle ID"),
    trip_id: UUID | None = Query(None, description="Filter by trip ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    search: str | None = Query(None, description="Search by station, location or receipt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "read"))
):
    """
    Get list of fuel records with pagination and filters.

    Permissions: fuel:read
    """
    service = FuelService(db)
    records, total = service.get_fuel_entries(
        page=page,
        page_size=page_size,
        vehicle_id=vehicle_id,
        trip_id=trip_id,
        start_date=start_date,
        end_date=end_date,
        search=search
    )

    return PaginatedResponse(
        success=True,
        data=[FuelListResponse.model_validate(r) for r in records],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post(
    "",
    response_model=FuelResponse,
    status_code=status.HTTP_201_CREATED
)
def create_fuel_entry(
    data: FuelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "create"))
):
    """
    Create a new fuel record.

    Permissions: fuel:create

    Business Rules:
    - Vehicle must exist and not be Retired
    - Fuel type must match vehicle's fuel type
    - Trip must exist if provided
    - Refuel date cannot be in the future
    - Odometer reading must be >= vehicle's current odometer
    - Total cost is auto-calculated
    """
    service = FuelService(db)
    record = service.create_fuel_entry(data, recorded_by=current_user.id)
    return FuelResponse.model_validate(record)


# ============================================================
# SINGLE RESOURCE ROUTES (parametric /{fuel_id})
# ============================================================

@router.get("/{fuel_id}", response_model=FuelResponse)
def get_fuel_entry(
    fuel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "read"))
):
    """
    Get fuel record by ID.

    Permissions: fuel:read
    """
    service = FuelService(db)
    record = service.get_fuel_entry(fuel_id)
    return FuelResponse.model_validate(record)


@router.put("/{fuel_id}", response_model=FuelResponse)
def update_fuel_entry(
    fuel_id: UUID,
    data: FuelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "update"))
):
    """
    Update a fuel record.

    Permissions: fuel:update
    """
    service = FuelService(db)
    record = service.update_fuel_entry(fuel_id, data, current_user)
    return FuelResponse.model_validate(record)


@router.delete("/{fuel_id}", response_model=SuccessResponse)
def delete_fuel_entry(
    fuel_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "delete"))
):
    """
    Delete a fuel record.

    Permissions: fuel:delete
    """
    service = FuelService(db)
    service.delete_fuel_entry(fuel_id, current_user)
    return SuccessResponse(
        success=True,
        message="Fuel record deleted successfully"
    )
