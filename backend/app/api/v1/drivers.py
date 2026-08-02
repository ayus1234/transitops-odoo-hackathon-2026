"""
Driver API endpoints.
Extended with Driver 360 profile endpoint.
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
    DriverListResponse,
    Driver360Response
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
    """
    service = DriverService(db)
    driver = service.create_driver(driver_data, current_user)
    return DriverResponse.model_validate(driver)


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


@router.get("/{driver_id}/360", response_model=Driver360Response)
def get_driver_360(
    driver_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("drivers", "read"))
):
    """
    Get comprehensive Driver 360 profile.

    Permissions: drivers:read
    """
    service = DriverService(db)
    profile = service.get_driver_360(driver_id)
    return Driver360Response(
        driver=DriverResponse.model_validate(profile["driver"]),
        documents_count=profile["documents_count"],
        recent_trips_count=profile["recent_trips_count"]
    )


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

    return {
        "success": True,
        "data": {
            "driver_id": str(driver.id),
            "driver_name": driver.user.full_name,
            "total_trips": driver.total_trips,
            "safety_score": float(driver.safety_score),
            "efficiency_score": float(driver.efficiency_score or 100.0),
            "compliance_score": float(driver.compliance_score or 100.0),
            "overall_score": float(driver.overall_score or 100.0),
            "license_valid": driver.is_license_valid,
            "medical_valid": driver.is_medical_valid,
            "status": driver.status
        }
    }


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
    """
    service = DriverService(db)
    driver = service.update_driver(driver_id, driver_data, current_user)
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
    """
    service = DriverService(db)
    service.delete_driver(driver_id, current_user)
    return SuccessResponse(
        success=True,
        message="Driver deleted successfully"
    )
