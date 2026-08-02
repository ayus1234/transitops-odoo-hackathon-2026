"""
Vehicle service layer containing business logic.
Extended with Vehicle 360 profile and lifecycle management.
"""
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle, VEHICLE_STATUSES
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleStatusUpdate
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

    def create_vehicle(self, vehicle_data: VehicleCreate, current_user: Optional[User] = None) -> Vehicle:
        """
        Create a new vehicle.

        Business Rules:
        - Registration number must be unique
        - VIN must be unique (if provided)
        - Capacity must be positive

        Raises:
            DuplicateEntryError: If registration number already exists
        """
        # Check if registration number already exists
        if self.repository.exists_by_registration(vehicle_data.registration_number):
            raise DuplicateEntryError(
                f"Vehicle with registration number '{vehicle_data.registration_number}' already exists"
            )

        # Check VIN uniqueness if provided
        if vehicle_data.vin and self.repository.exists_by_vin(vehicle_data.vin):
            raise DuplicateEntryError(
                f"Vehicle with VIN '{vehicle_data.vin}' already exists"
            )

        # Create vehicle
        vehicle = self.repository.create(vehicle_data)

        # Log activity
        if current_user is not None:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.VEHICLE,
                activity_type=ActivityTypeEnum.CREATED,
                title=f"Vehicle {vehicle.registration_number} registered successfully",
                description=f"New vehicle {vehicle.vehicle_name} ({vehicle.vehicle_type}) added to fleet.",
                severity=SeverityEnum.SUCCESS,
                status="Success",
                user_id=str(current_user.id),
                vehicle_id=str(vehicle.id)
            ))

        return vehicle

    def update_vehicle(self, vehicle_id: UUID, vehicle_data: VehicleUpdate, current_user: Optional[User] = None) -> Vehicle:
        """
        Update an existing vehicle.

        Business Rules:
        - Cannot change registration to existing one
        - Cannot change VIN to existing one
        - Status changes go through lifecycle validation

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

        # Check VIN uniqueness if being updated
        if vehicle_data.vin and vehicle_data.vin != getattr(vehicle, 'vin', None):
            if self.repository.exists_by_vin(vehicle_data.vin, exclude_id=vehicle_id):
                raise DuplicateEntryError(
                    f"Vehicle with VIN '{vehicle_data.vin}' already exists"
                )

        # Validate status change if provided
        current_status = vehicle.status
        if vehicle_data.status and vehicle_data.status != vehicle.status:
            self._validate_status_change(vehicle, vehicle_data.status)

        updated_vehicle = self.repository.update(vehicle, vehicle_data)

        if current_user is not None:
            # Check for specific status changes or general updates
            if vehicle_data.status and vehicle_data.status != current_status:
                title = f"Vehicle {updated_vehicle.registration_number} status changed"
                desc = f"Status updated from {current_status} to {vehicle_data.status}."
                act_type = ActivityTypeEnum.SYSTEM if vehicle_data.status in ('In Shop', 'Maintenance') else ActivityTypeEnum.UPDATED
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
                user_id=str(current_user.id),
                vehicle_id=str(updated_vehicle.id)
            ))

        return updated_vehicle

    def update_vehicle_status(
        self,
        vehicle_id: UUID,
        status_data: VehicleStatusUpdate,
        current_user: Optional[User] = None
    ) -> Vehicle:
        """
        Explicit lifecycle status transition with validation.

        Validates that the transition is allowed by the lifecycle state machine,
        then applies the status change along with any associated metadata
        (retired_date, sale_price).

        Raises:
            NotFoundError: If vehicle not found
            BusinessLogicError: If transition is not allowed
        """
        vehicle = self.get_vehicle(vehicle_id)
        old_status = vehicle.status

        if not vehicle.can_transition_to(status_data.new_status):
            allowed = vehicle.get_allowed_transitions()
            raise BusinessLogicError(
                f"Cannot transition vehicle from '{old_status}' to '{status_data.new_status}'. "
                f"Allowed transitions: {', '.join(allowed) if allowed else 'none'}.",
                code="BIZ_LIFECYCLE_001"
            )

        # Apply status
        vehicle.status = status_data.new_status

        # Apply associated metadata
        if status_data.new_status in ('Retired', 'Sold') and status_data.retired_date:
            vehicle.retired_date = status_data.retired_date
        if status_data.new_status == 'Sold' and status_data.sale_price is not None:
            vehicle.sale_price = float(status_data.sale_price)

        self.db.commit()
        self.db.refresh(vehicle)

        # Log activity
        if current_user is not None:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.VEHICLE,
                activity_type=ActivityTypeEnum.UPDATED,
                title=f"Vehicle {vehicle.registration_number} lifecycle: {old_status} → {status_data.new_status}",
                description=status_data.reason or f"Status transitioned from {old_status} to {status_data.new_status}.",
                severity=SeverityEnum.INFO if status_data.new_status not in ('Retired', 'Sold') else SeverityEnum.WARNING,
                status="Success",
                user_id=str(current_user.id),
                vehicle_id=str(vehicle.id)
            ))

        return vehicle

    def get_vehicle_360(self, vehicle_id: UUID) -> dict:
        """
        Get comprehensive Vehicle 360 profile.

        Aggregates:
        - Full vehicle record with all 360 fields
        - Allowed lifecycle transitions
        - (Future: odometer history, documents, maintenance, trips, expenses, TCO)
        """
        vehicle = self.get_vehicle(vehicle_id)
        return {
            "vehicle": vehicle,
            "allowed_transitions": vehicle.get_allowed_transitions(),
        }

    def delete_vehicle(self, vehicle_id: UUID, current_user: Optional[User] = None) -> None:
        """
        Delete a vehicle.

        Business Rules:
        - Cannot delete vehicle that is On Trip, In Shop, or in Maintenance

        Raises:
            NotFoundError: If vehicle not found
            BusinessLogicError: If vehicle is in use
        """
        vehicle = self.get_vehicle(vehicle_id)

        # Check if vehicle can be deleted
        if vehicle.status in ['On Trip', 'In Shop', 'Maintenance', 'Active', 'Assigned']:
            raise BusinessLogicError(
                f"Cannot delete vehicle that is '{vehicle.status}'. "
                "Complete or cancel active operations first.",
                code="BIZ_001"
            )


        # Log before deletion
        reg_number = vehicle.registration_number
        if current_user is not None:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.VEHICLE,
                activity_type=ActivityTypeEnum.DELETED,
                title=f"Vehicle {reg_number} deleted",
                description="Vehicle removed from active registry.",
                severity=SeverityEnum.WARNING,
                status="Success",
                user_id=str(current_user.id)
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
        Validate status change business rules using lifecycle state machine.

        Rules:
        - Manual status changes to 'On Trip' are not allowed (only through trip dispatch)
        - All other transitions must follow the lifecycle state machine
        """
        # Cannot manually set to 'On Trip' — only via trip dispatch
        if new_status == 'On Trip':
            raise BusinessLogicError(
                "Cannot manually set vehicle status to 'On Trip'. "
                "Use trip dispatch to assign vehicle.",
                code="BIZ_007"
            )

        # Validate lifecycle transition
        if not vehicle.can_transition_to(new_status):
            allowed = vehicle.get_allowed_transitions()
            raise BusinessLogicError(
                f"Cannot change status from '{vehicle.status}' to '{new_status}'. "
                f"Allowed transitions: {', '.join(allowed) if allowed else 'none'}.",
                code="BIZ_LIFECYCLE_001"
            )
