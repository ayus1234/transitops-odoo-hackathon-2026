"""
Maintenance API endpoints.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceStatusUpdate,
    MaintenanceComplete,
    MaintenanceResponse,
    MaintenanceListResponse,
    CalendarEventResponse,
    MaintenanceReschedule
)
from datetime import date, timedelta
from typing import List
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.maintenance_service import MaintenanceService


router = APIRouter()


# ============================================================
# STATIC ROUTES (must come before /{maintenance_id})
# ============================================================

@router.get("/statistics/status", response_model=dict)
def get_maintenance_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """
    Get maintenance statistics by status.

    Permissions: maintenance:read
    """
    service = MaintenanceService(db)
    return {
        "success": True,
        "data": service.get_statistics()
    }


# ============================================================
# SCHEDULER ROUTES
# ============================================================

@router.get("/scheduler", response_model=SuccessResponse)
def get_scheduler_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get all maintenance calendar events."""
    service = MaintenanceService(db)
    events = service.get_scheduler_events(current_user=current_user)
    return SuccessResponse(success=True, message="Success", data=events)

@router.get("/scheduler/month", response_model=SuccessResponse)
def get_scheduler_month_view(
    year: int = Query(..., description="Year"),
    month: int = Query(..., description="Month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get maintenance calendar events for a specific month."""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
        
    service = MaintenanceService(db)
    events = service.get_scheduler_events(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date
    )
    return SuccessResponse(success=True, message="Success", data=events)

@router.get("/scheduler/week", response_model=SuccessResponse)
def get_scheduler_week_view(
    start_date: date = Query(..., description="Start date of the week"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get maintenance calendar events for a week."""
    end_date = start_date + timedelta(days=6)
    service = MaintenanceService(db)
    events = service.get_scheduler_events(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date
    )
    return SuccessResponse(success=True, message="Success", data=events)

@router.get("/scheduler/day", response_model=SuccessResponse)
def get_scheduler_day_view(
    day_date: date = Query(..., description="Date for day view"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get maintenance calendar events for a specific day."""
    service = MaintenanceService(db)
    events = service.get_scheduler_events(
        current_user=current_user,
        start_date=day_date,
        end_date=day_date
    )
    return SuccessResponse(success=True, message="Success", data=events)

@router.get("/scheduler/upcoming", response_model=SuccessResponse)
def get_upcoming_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get upcoming maintenance jobs (Scheduled and In Progress)."""
    service = MaintenanceService(db)
    events = service.get_scheduler_events(current_user=current_user)
    upcoming = [e for e in events if e.status in ['Scheduled', 'In Progress'] and e.scheduled_date >= date.today()]
    return SuccessResponse(success=True, message="Success", data=upcoming)

@router.get("/scheduler/completed", response_model=SuccessResponse)
def get_completed_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get completed maintenance jobs."""
    service = MaintenanceService(db)
    events = service.get_scheduler_events(current_user=current_user, status='Completed')
    return SuccessResponse(success=True, message="Success", data=events)

@router.get("/scheduler/search", response_model=SuccessResponse)
def search_scheduler_events(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Search maintenance calendar events."""
    service = MaintenanceService(db)
    events = service.get_scheduler_events(current_user=current_user, search=q)
    return SuccessResponse(success=True, message="Success", data=events)

@router.get("/scheduler/filter", response_model=SuccessResponse)
def filter_scheduler_events(
    status: str | None = None,
    priority: str | None = None,
    vehicle_id: UUID | None = None,
    technician: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Filter maintenance calendar events."""
    service = MaintenanceService(db)
    events = service.get_scheduler_events(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        status=status,
        priority=priority,
        vehicle_id=vehicle_id,
        technician=technician
    )
    return SuccessResponse(success=True, message="Success", data=events)

@router.put("/scheduler/{maintenance_id}/reschedule", response_model=SuccessResponse)
def reschedule_maintenance(
    maintenance_id: UUID,
    data: MaintenanceReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "update"))
):
    """Reschedule a maintenance event."""
    service = MaintenanceService(db)
    event = service.reschedule_event(maintenance_id, data, current_user)
    return SuccessResponse(success=True, message="Maintenance rescheduled successfully", data=event)


# ============================================================
# COLLECTION ROUTES
# ============================================================

@router.get("", response_model=PaginatedResponse[MaintenanceListResponse])
def list_maintenance(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    vehicle_id: UUID | None = Query(None, description="Filter by vehicle ID"),
    priority: str | None = Query(None, description="Filter by priority"),
    search: str | None = Query(
        None, description="Search by number, type, description, or technician"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """
    Get list of maintenance records with pagination and filters.

    Permissions: maintenance:read
    """
    service = MaintenanceService(db)
    records, total = service.get_maintenance_list(
        page=page,
        page_size=page_size,
        status=status,
        vehicle_id=vehicle_id,
        priority=priority,
        search=search
    )

    return PaginatedResponse(
        success=True,
        data=[MaintenanceListResponse.model_validate(r) for r in records],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_maintenance(
    data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "create"))
):
    """
    Create a new maintenance record.

    Permissions: maintenance:create

    Business Rules:
    - Vehicle must exist and not be Retired
    - Estimated cost and odometer cannot be negative
    """
    service = MaintenanceService(db)
    record = service.create_maintenance(data, created_by=current_user.id)
    return MaintenanceResponse.model_validate(record)


# ============================================================
# SINGLE RESOURCE ROUTES (parametric /{maintenance_id})
# ============================================================

@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def get_maintenance(
    maintenance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """
    Get maintenance record by ID.

    Permissions: maintenance:read
    """
    service = MaintenanceService(db)
    record = service.get_maintenance(maintenance_id)
    return MaintenanceResponse.model_validate(record)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def update_maintenance(
    maintenance_id: UUID,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "update"))
):
    """
    Update a maintenance record.

    Permissions: maintenance:update

    Business Rules:
    - Can only update records in Pending or Approved status
    """
    service = MaintenanceService(db)
    record = service.update_maintenance(maintenance_id, data, current_user)
    return MaintenanceResponse.model_validate(record)


@router.delete("/{maintenance_id}", response_model=SuccessResponse)
def delete_maintenance(
    maintenance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "delete"))
):
    """
    Delete a maintenance record.

    Permissions: maintenance:delete

    Business Rules:
    - Cannot delete In Progress or Completed records
    """
    service = MaintenanceService(db)
    service.delete_maintenance(maintenance_id, current_user)
    return SuccessResponse(
        success=True,
        message="Maintenance record deleted successfully"
    )


# ============================================================
# LIFECYCLE ACTION ROUTES
# ============================================================

@router.patch(
    "/{maintenance_id}/status",
    response_model=MaintenanceResponse
)
def update_maintenance_status(
    maintenance_id: UUID,
    data: MaintenanceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "update"))
):
    """
    Update maintenance status.

    Permissions: maintenance:update

    Business Logic:
    - If status → 'In Progress': sets vehicle.status = 'In Shop'
    - If status → 'Completed': restores vehicle.status = 'Available'
    - Only valid status transitions allowed
    """
    service = MaintenanceService(db)
    record = service.update_status(maintenance_id, data, current_user)
    return MaintenanceResponse.model_validate(record)


@router.post(
    "/{maintenance_id}/complete",
    response_model=MaintenanceResponse
)
def complete_maintenance(
    maintenance_id: UUID,
    data: MaintenanceComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "update"))
):
    """
    Complete a maintenance record.

    Permissions: maintenance:update

    Business Logic:
    - Sets status to 'Completed'
    - Records actual cost and completion date
    - Restores vehicle.status to 'Available'
    """
    service = MaintenanceService(db)
    record = service.complete_maintenance(maintenance_id, data, current_user)
    return MaintenanceResponse.model_validate(record)
