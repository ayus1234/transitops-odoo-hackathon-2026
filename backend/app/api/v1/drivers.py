"""
Driver API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.driver import (
    DriverCreate,
    DriverUpdate,
    DriverResponse,
    DriverListResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.driver_service import DriverService


router = APIRouter()


@router.get("", response_model=PaginatedResponse[DriverListResponse])
def list_drivers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search by name, license, or email"),
    license_expiring_soon: bool = Query(False, description="Filter drivers with licenses expiring within 30 days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get list of drivers with pagination and filters.
    
    Permissions: drivers:read
    """
    service = DriverService(db)
    drivers, total = service.get_drivers(
        page=page,
        page_size=page_size,
        status=status,
        search=search,
        license_expiring_soon=license_expiring_soon
    )
    
    return PaginatedResponse(
        success=True,
        data=[DriverListResponse.model_validate(d) for d in drivers],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver_data: DriverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "create"))
):
    """
    Create a new driver with user account.
    
    Permissions: drivers:create
    
    Business Rules:
    - License number must be unique
    - User email must be unique
    - Driver must be at least 18 years old
    - License must not be expired
    - License expiry date must be after issue date
    """
    service = DriverService(db)
    driver = service.create_driver(driver_data)
    return DriverResponse.model_validate(driver)


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get driver by ID.
    
    Permissions: drivers:read
    """
    service = DriverService(db)
    driver = service.get_driver(driver_id)
    return DriverResponse.model_validate(driver)


@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: UUID,
    driver_data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "update"))
):
    """
    Update an existing driver.
    
    Permissions: drivers:update
    
    Business Rules:
    - Cannot change license to existing one
    - Cannot manually change status to 'On Trip'
    - Cannot change status while 'On Trip'
    - License dates must be valid
    """
    service = DriverService(db)
    driver = service.update_driver(driver_id, driver_data)
    return DriverResponse.model_validate(driver)


@router.delete("/{driver_id}", response_model=SuccessResponse)
def delete_driver(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "delete"))
):
    """
    Delete a driver and associated user account.
    
    Permissions: drivers:delete
    
    Business Rules:
    - Cannot delete driver that is 'On Trip'
    """
    service = DriverService(db)
    service.delete_driver(driver_id)
    return SuccessResponse(
        success=True,
        message="Driver deleted successfully"
    )


@router.get("/available/list", response_model=List[DriverListResponse])
def get_available_drivers(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get all available drivers with valid licenses for trip assignment.
    
    Permissions: drivers:read
    """
    service = DriverService(db)
    drivers = service.get_available_drivers()
    return [DriverListResponse.model_validate(d) for d in drivers]


@router.get("/expiring-licenses/list", response_model=List[DriverListResponse])
def get_drivers_with_expiring_licenses(
    days: int = Query(30, ge=1, le=90, description="Days until license expiry"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get drivers whose licenses are expiring within specified days.
    
    Permissions: drivers:read
    """
    service = DriverService(db)
    drivers = service.get_drivers_with_expiring_licenses(days)
    return [DriverListResponse.model_validate(d) for d in drivers]


@router.get("/statistics/status", response_model=dict)
def get_driver_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get driver statistics by status.
    
    Permissions: drivers:read
    """
    service = DriverService(db)
    return {
        "success": True,
        "data": service.get_driver_statistics()
    }


@router.get("/{driver_id}/performance", response_model=dict)
def get_driver_performance(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get driver performance metrics.
    
    Permissions: drivers:read
    """
    service = DriverService(db)
    driver = service.get_driver(driver_id)
    
    # Basic performance data (can be enhanced with trip data later)
    return {
        "success": True,
        "data": {
            "driver_id": str(driver.id),
            "driver_name": driver.user.full_name,
            "total_trips": driver.total_trips,
            "safety_score": float(driver.safety_score),
            "license_valid": driver.is_license_valid,
            "status": driver.status
        }
    }
