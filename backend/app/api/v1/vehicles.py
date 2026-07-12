"""
Vehicle API endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleListResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.vehicle_service import VehicleService


router = APIRouter()


@router.get("", response_model=PaginatedResponse[VehicleListResponse])
def list_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status"),
    vehicle_type: str | None = Query(None, description="Filter by vehicle type"),
    search: str | None = Query(None, description="Search by registration or name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """
    Get list of vehicles with pagination and filters.
    
    Permissions: vehicles:read
    """
    service = VehicleService(db)
    vehicles, total = service.get_vehicles(
        page=page,
        page_size=page_size,
        status=status,
        vehicle_type=vehicle_type,
        search=search
    )
    
    return PaginatedResponse(
        success=True,
        data=[VehicleListResponse.model_validate(v) for v in vehicles],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "create"))
):
    """
    Create a new vehicle.
    
    Permissions: vehicles:create
    
    Business Rules:
    - Registration number must be unique
    - Capacity must be positive
    """
    service = VehicleService(db)
    vehicle = service.create_vehicle(vehicle_data)
    return VehicleResponse.model_validate(vehicle)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """
    Get vehicle by ID.
    
    Permissions: vehicles:read
    """
    service = VehicleService(db)
    vehicle = service.get_vehicle(vehicle_id)
    return VehicleResponse.model_validate(vehicle)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "update"))
):
    """
    Update an existing vehicle.
    
    Permissions: vehicles:update
    
    Business Rules:
    - Cannot change registration to existing one
    - Cannot manually change status to 'On Trip'
    - Cannot change status while 'On Trip'
    """
    service = VehicleService(db)
    vehicle = service.update_vehicle(vehicle_id, vehicle_data)
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}", response_model=SuccessResponse)
def delete_vehicle(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "delete"))
):
    """
    Delete a vehicle.
    
    Permissions: vehicles:delete
    
    Business Rules:
    - Cannot delete vehicle that is 'On Trip' or 'In Shop'
    """
    service = VehicleService(db)
    service.delete_vehicle(vehicle_id)
    return SuccessResponse(
        success=True,
        message="Vehicle deleted successfully"
    )


@router.get("/available/list", response_model=List[VehicleListResponse])
def get_available_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """
    Get all available vehicles for trip assignment.
    
    Permissions: vehicles:read
    """
    service = VehicleService(db)
    vehicles = service.get_available_vehicles()
    return [VehicleListResponse.model_validate(v) for v in vehicles]


@router.get("/statistics/status", response_model=dict)
def get_vehicle_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """
    Get vehicle statistics by status.
    
    Permissions: vehicles:read
    """
    service = VehicleService(db)
    return {
        "success": True,
        "data": service.get_vehicle_statistics()
    }
