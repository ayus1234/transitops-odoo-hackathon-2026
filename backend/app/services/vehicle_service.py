"""
Vehicle service layer containing business logic.
"""
from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.repositories.vehicle_repository import VehicleRepository
from app.utils.exceptions import (
    NotFoundError,
    DuplicateEntryError,
    BusinessLogicError
)
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User


class VehicleService:
    """Service for vehicle business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = VehicleRepository(db)
    
    def get_vehicle(self, vehicle_id: UUID) -> Vehicle:
        """
        Get vehicle by ID.
        
        Raises:
            NotFoundError: If vehicle not found
        """
        vehicle = self.repository.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle with ID {vehicle_id} not found")
        return vehicle
    
    def get_vehicles(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        vehicle_type: str | None = None,
        search: str | None = None
    ) -> Tuple[List[Vehicle], int]:
        """
        Get all vehicles with pagination and filters.
        
        Returns:
            Tuple of (vehicles list, total count)
        """
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            status=status,
            vehicle_type=vehicle_type,
            search=search
        )
    
    def create_vehicle(self, vehicle_data: VehicleCreate, current_user: User = None) -> Vehicle:
        """
        Create a new vehicle.
        
        Business Rules:
        - Registration number must be unique
        - Capacity must be positive
        
        Raises:
            DuplicateEntryError: If registration number already exists
        """
        # Check if registration number already exists
        if self.repository.exists_by_registration(vehicle_data.registration_number):
            raise DuplicateEntryError(
                f"Vehicle with registration number '{vehicle_data.registration_number}' already exists"
            )
        
        # Create vehicle
        vehicle = self.repository.create(vehicle_data)
        
        # Log activity
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.VEHICLE,
                activity_type=ActivityTypeEnum.CREATED,
                title=f"Vehicle {vehicle.registration_number} registered successfully",
                description=f"New vehicle {vehicle.vehicle_name} ({vehicle.vehicle_type}) added to fleet.",
                severity=SeverityEnum.SUCCESS,
                status="Success",
                user_id=current_user.id,
                vehicle_id=vehicle.id
            ))
            
        return vehicle
    
    def update_vehicle(self, vehicle_id: UUID, vehicle_data: VehicleUpdate, current_user: User = None) -> Vehicle:
        """
        Update an existing vehicle.
        
        Business Rules:
        - Cannot change registration to existing one
        - Cannot change status to 'On Trip' manually (only through trip dispatch)
        
        Raises:
            NotFoundError: If vehicle not found
            DuplicateEntryError: If new registration number already exists
            BusinessLogicError: If business rule violated
        """
        vehicle = self.get_vehicle(vehicle_id)
        
        # Check registration number uniqueness if being updated
        if (vehicle_data.registration_number and
            vehicle_data.registration_number != vehicle.registration_number):
            if self.repository.exists_by_registration(
                vehicle_data.registration_number,
                exclude_id=vehicle_id
            ):
                raise DuplicateEntryError(
                    f"Vehicle with registration number '{vehicle_data.registration_number}' already exists"
                )
        
        # Validate status change
        current_status = vehicle.status
        if vehicle_data.status and vehicle_data.status != vehicle.status:
            self._validate_status_change(vehicle, vehicle_data.status)
        
        updated_vehicle = self.repository.update(vehicle, vehicle_data)
        
        if current_user:
            # Check for specific status changes or general updates
            if vehicle_data.status and vehicle_data.status != current_status:
                title = f"Vehicle {updated_vehicle.registration_number} status changed"
                desc = f"Status updated to {vehicle_data.status}."
                act_type = ActivityTypeEnum.SYSTEM if vehicle_data.status == 'In Shop' else ActivityTypeEnum.UPDATED
            else:
                title = f"Vehicle {updated_vehicle.registration_number} updated"
                desc = "Vehicle registry details modified."
                act_type = ActivityTypeEnum.UPDATED
                
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.VEHICLE,
                activity_type=act_type,
                title=title,
                description=desc,
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id,
                vehicle_id=updated_vehicle.id
            ))
            
        return updated_vehicle
    
    def delete_vehicle(self, vehicle_id: UUID, current_user: User = None) -> None:
        """
        Delete a vehicle.
        
        Business Rules:
        - Cannot delete vehicle that is On Trip or In Shop
        
        Raises:
            NotFoundError: If vehicle not found
            BusinessLogicError: If vehicle is in use
        """
        vehicle = self.get_vehicle(vehicle_id)
        
        # Check if vehicle can be deleted
        if vehicle.status in ['On Trip', 'In Shop']:
            raise BusinessLogicError(
                f"Cannot delete vehicle that is '{vehicle.status}'. "
                "Complete or cancel active operations first.",
                code="BIZ_001"
            )
        
        
        # Log before deletion
        reg_number = vehicle.registration_number
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.VEHICLE,
                activity_type=ActivityTypeEnum.DELETED,
                title=f"Vehicle {reg_number} deleted",
                description="Vehicle removed from active registry.",
                severity=SeverityEnum.WARNING,
                status="Success",
                user_id=current_user.id
            ))
            
        self.repository.delete(vehicle)
    
    def get_available_vehicles(self) -> List[Vehicle]:
        """Get all vehicles available for assignment."""
        return self.repository.get_available_vehicles()
    
    def get_vehicle_statistics(self) -> dict:
        """Get vehicle statistics by status."""
        return self.repository.count_by_status()
    
    def _validate_status_change(self, vehicle: Vehicle, new_status: str) -> None:
        """
        Validate status change business rules.
        
        Rules:
        - Manual status changes to 'On Trip' are not allowed
        - Can only change to 'Available' from 'In Shop' or 'Retired'
        - Can change to 'In Shop' from 'Available'
        - Can change to 'Retired' from any status except 'On Trip'
        """
        current_status = vehicle.status
        
        # Cannot manually set to 'On Trip'
        if new_status == 'On Trip':
            raise BusinessLogicError(
                "Cannot manually set vehicle status to 'On Trip'. "
                "Use trip dispatch to assign vehicle.",
                code="BIZ_007"
            )
        
        # Cannot change from 'On Trip' directly
        if current_status == 'On Trip':
            raise BusinessLogicError(
                f"Cannot change status from 'On Trip' to '{new_status}'. "
                "Complete or cancel the trip first.",
                code="BIZ_001"
            )
        
        # Validate 'In Shop' transition
        if new_status == 'In Shop' and current_status not in ['Available']:
            raise BusinessLogicError(
                f"Cannot change status from '{current_status}' to 'In Shop'. "
                "Vehicle must be 'Available' first.",
                code="BIZ_007"
            )
