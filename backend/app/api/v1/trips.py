"""
Trip API endpoints.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.trip import (
    TripCreate,
    TripUpdate,
    TripDispatch,
    TripComplete,
    TripCancel,
    TripResponse,
    TripListResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.trip_service import TripService


router = APIRouter()


# ============================================================
# STATIC ROUTES (must come before /{trip_id} parametric routes)
# ============================================================

@router.get("/statistics/status", response_model=dict)
def get_trip_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """
    Get trip statistics by status.
    
    Permissions: trips:read
    """
    service = TripService(db)
    return {
        "success": True,
        "data": service.get_trip_statistics()
    }


# ============================================================
# COLLECTION ROUTES
# ============================================================

@router.get("", response_model=PaginatedResponse[TripListResponse])
def list_trips(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    vehicle_id: UUID | None = Query(None, description="Filter by vehicle ID"),
    driver_id: UUID | None = Query(None, description="Filter by driver ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    search: str | None = Query(None, description="Search by trip number, source, or destination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """
    Get list of trips with pagination and filters.
    
    Permissions: trips:read
    """
    service = TripService(db)
    trips, total = service.get_trips(
        page=page,
        page_size=page_size,
        status=status,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
        search=search
    )
    
    return PaginatedResponse(
        success=True,
        data=[TripListResponse.model_validate(t) for t in trips],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "create"))
):
    """
    Create a new trip.
    
    Permissions: trips:create
    
    Business Rules:
    - Vehicle must exist and be available
    - Driver must exist, be available, and have a valid license
    - Cargo weight cannot exceed vehicle capacity
    - Vehicle and driver must not be on another active trip
    - Planned arrival must be after planned departure
    """
    service = TripService(db)
    trip = service.create_trip(trip_data, created_by=current_user.id)
    return TripResponse.model_validate(trip)


# ============================================================
# SINGLE RESOURCE ROUTES (parametric /{trip_id})
# ============================================================

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """
    Get trip by ID.
    
    Permissions: trips:read
    """
    service = TripService(db)
    trip = service.get_trip(trip_id)
    return TripResponse.model_validate(trip)


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: UUID,
    trip_data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """
    Update an existing trip.
    
    Permissions: trips:update
    
    Business Rules:
    - Can only update trips in Draft status
    - All creation validations apply to changed fields
    """
    service = TripService(db)
    trip = service.update_trip(trip_id, trip_data)
    return TripResponse.model_validate(trip)


@router.delete("/{trip_id}", response_model=SuccessResponse)
def delete_trip(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "delete"))
):
    """
    Delete a trip.
    
    Permissions: trips:delete
    
    Business Rules:
    - Cannot delete Dispatched or Completed trips
    """
    service = TripService(db)
    service.delete_trip(trip_id)
    return SuccessResponse(
        success=True,
        message="Trip deleted successfully"
    )


# ============================================================
# LIFECYCLE ACTION ROUTES
# ============================================================

@router.post("/{trip_id}/dispatch", response_model=TripResponse)
def dispatch_trip(
    trip_id: UUID,
    dispatch_data: TripDispatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """
    Dispatch a trip.
    
    Permissions: trips:update
    
    Business Logic:
    - Changes trip status to 'Dispatched'
    - Sets vehicle status to 'On Trip'
    - Sets driver status to 'On Trip'
    - Records actual departure time and start odometer
    """
    service = TripService(db)
    trip = service.dispatch_trip(trip_id, dispatch_data)
    return TripResponse.model_validate(trip)


@router.post("/{trip_id}/complete", response_model=TripResponse)
def complete_trip(
    trip_id: UUID,
    complete_data: TripComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """
    Complete a trip.
    
    Permissions: trips:update
    
    Business Logic:
    - Changes trip status to 'Completed'
    - Restores vehicle status to 'Available'
    - Restores driver status to 'Available'
    - Increments driver total_trips
    - Updates vehicle odometer
    """
    service = TripService(db)
    trip = service.complete_trip(trip_id, complete_data)
    return TripResponse.model_validate(trip)


@router.post("/{trip_id}/cancel", response_model=TripResponse)
def cancel_trip(
    trip_id: UUID,
    cancel_data: TripCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """
    Cancel a trip.
    
    Permissions: trips:update
    
    Business Logic:
    - Changes trip status to 'Cancelled'
    - If trip was Dispatched, restores vehicle and driver to 'Available'
    """
    service = TripService(db)
    trip = service.cancel_trip(trip_id, cancel_data)
    return TripResponse.model_validate(trip)
