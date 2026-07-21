"""
Maintenance service layer containing business logic.
"""
from datetime import date
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.maintenance import Maintenance
from app.models.vehicle import Vehicle
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceStatusUpdate,
    MaintenanceComplete,
    CalendarEventResponse,
    MaintenanceReschedule
)
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.utils.exceptions import (
    NotFoundError,
    BusinessLogicError,
)
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User


class MaintenanceService:
    """Service for maintenance business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = MaintenanceRepository(db)
        self.vehicle_repository = VehicleRepository(db)

    # ============================================================
    # READ
    # ============================================================

    def get_maintenance(self, maintenance_id: UUID) -> Maintenance:
        """
        Get maintenance by ID.

        Raises:
            NotFoundError: If maintenance not found
        """
        record = self.repository.get_by_id(maintenance_id)
        if not record:
            raise NotFoundError(
                f"Maintenance record with ID {maintenance_id} not found"
            )
        return record

    def get_maintenance_list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        vehicle_id: UUID | None = None,
        priority: str | None = None,
        search: str | None = None
    ) -> Tuple[List[Maintenance], int]:
        """
        Get all maintenance records with pagination and filters.

        Returns:
            Tuple of (records list, total count)
        """
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            status=status,
            vehicle_id=vehicle_id,
            priority=priority,
            search=search
        )

    # ============================================================
    # CREATE
    # ============================================================

    def create_maintenance(
        self,
        data: MaintenanceCreate,
        created_by: UUID | None = None
    ) -> Maintenance:
        """
        Create a new maintenance record.

        Business Rules:
        - Vehicle must exist
        - Vehicle must not be Retired
        - Estimated cost cannot be negative (enforced by schema)
        - Odometer reading cannot be negative (enforced by schema)

        Raises:
            NotFoundError: If vehicle not found
            BusinessLogicError: If business rules violated
        """
        # 1. Validate vehicle exists
        vehicle = self.vehicle_repository.get_by_id(data.vehicle_id)
        if not vehicle:
            raise NotFoundError(
                f"Vehicle with ID {data.vehicle_id} not found"
            )

        # 2. Validate vehicle is not retired
        if not vehicle.is_operational:
            raise BusinessLogicError(
                f"Vehicle '{vehicle.registration_number}' is retired "
                "and cannot have new maintenance scheduled.",
                code="BIZ_020"
            )

        # Generate maintenance number
        maintenance_number = self.repository.get_next_maintenance_number()

        # Build data dict
        record_dict = data.model_dump()
        record_dict["maintenance_number"] = maintenance_number
        record_dict["status"] = "Pending"
        if created_by:
            record_dict["created_by"] = created_by

        record = self.repository.create(record_dict)
        
        if created_by:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.MAINTENANCE,
                activity_type=ActivityTypeEnum.CREATED,
                title="Maintenance Requested",
                description=f"Maintenance {record.maintenance_number} scheduled for vehicle {vehicle.registration_number}.",
                severity=SeverityEnum.WARNING,
                status="Pending",
                user_id=created_by,
                vehicle_id=vehicle.id,
                maintenance_id=record.id
            ))
            
        return record

    # ============================================================
    # UPDATE
    # ============================================================

    def update_maintenance(
        self,
        maintenance_id: UUID,
        data: MaintenanceUpdate,
        current_user: User = None
    ) -> Maintenance:
        """
        Update a maintenance record.

        Business Rules:
        - Can only update records in Pending or Approved status
        - Cannot change core fields once In Progress or Completed

        Raises:
            NotFoundError: If not found
            BusinessLogicError: If business rules violated
        """
        record = self.get_maintenance(maintenance_id)

        if record.status not in ('Pending', 'Approved'):
            raise BusinessLogicError(
                f"Cannot update maintenance '{record.maintenance_number}' "
                f"with status '{record.status}'. "
                "Only Pending or Approved records can be updated.",
                code="BIZ_021"
            )

        update_data = data.model_dump(exclude_unset=True)

        # If vehicle is being re-validated via estimated_cost or odometer
        # no extra checks needed — schema handles >= 0

        updated_record = self.repository.update(record, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.MAINTENANCE,
                activity_type=ActivityTypeEnum.UPDATED,
                title=f"Maintenance {updated_record.maintenance_number} updated",
                description="Maintenance details were modified.",
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id,
                maintenance_id=updated_record.id,
                vehicle_id=updated_record.vehicle_id
            ))
            
        return updated_record

    # ============================================================
    # STATUS TRANSITIONS
    # ============================================================

    # Valid transitions map
    _STATUS_TRANSITIONS = {
        'Pending': ['Approved', 'Rejected'],
        'Approved': ['In Progress', 'Rejected'],
        'In Progress': ['Completed'],
        'Completed': [],
        'Rejected': [],
    }

    def update_status(
        self,
        maintenance_id: UUID,
        data: MaintenanceStatusUpdate,
        current_user: User = None
    ) -> Maintenance:
        """
        Update maintenance status with business logic side-effects.

        Business Rules:
        - Only valid status transitions allowed
        - 'In Progress' → sets vehicle.status = 'In Shop'
        - 'Completed' → restores vehicle.status = 'Available'
        - Vehicle cannot start maintenance if already On Trip

        Raises:
            NotFoundError: If not found
            BusinessLogicError: If transition is invalid
        """
        record = self.get_maintenance(maintenance_id)
        new_status = data.status

        # Validate transition
        allowed = self._STATUS_TRANSITIONS.get(record.status, [])
        if new_status not in allowed:
            raise BusinessLogicError(
                f"Cannot transition maintenance '{record.maintenance_number}' "
                f"from '{record.status}' to '{new_status}'. "
                f"Allowed transitions: {', '.join(allowed) if allowed else 'none'}.",
                code="BIZ_022"
            )

        vehicle = self.vehicle_repository.get_by_id(record.vehicle_id)

        # Side-effect: In Progress → vehicle to 'In Shop'
        if new_status == 'In Progress':
            if vehicle.status == 'On Trip':
                raise BusinessLogicError(
                    f"Vehicle '{vehicle.registration_number}' is currently "
                    "On Trip and cannot be sent for maintenance. "
                    "Complete or cancel the trip first.",
                    code="BIZ_023"
                )
            vehicle.status = 'In Shop'

        # Side-effect: Completed → vehicle to 'Available'
        if new_status == 'Completed':
            if vehicle.status == 'In Shop':
                vehicle.status = 'Available'

        updated_record = self.repository.update(record, {"status": new_status})
        
        if current_user:
            title = f"Maintenance {new_status}"
            desc = f"Status updated to {new_status} for {vehicle.registration_number}."
            if new_status == 'Approved':
                act_type = ActivityTypeEnum.APPROVED
                severity = SeverityEnum.SUCCESS
            elif new_status == 'Rejected':
                act_type = ActivityTypeEnum.REJECTED
                severity = SeverityEnum.WARNING
            elif new_status == 'In Progress':
                act_type = ActivityTypeEnum.SYSTEM
                severity = SeverityEnum.INFO
                title = "Maintenance Started"
            else:
                act_type = ActivityTypeEnum.UPDATED
                severity = SeverityEnum.INFO
                
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.MAINTENANCE,
                activity_type=act_type,
                title=title,
                description=desc,
                severity=severity,
                status="Success",
                user_id=current_user.id,
                maintenance_id=updated_record.id,
                vehicle_id=vehicle.id
            ))
            
        return updated_record

    # ============================================================
    # COMPLETE
    # ============================================================

    def complete_maintenance(
        self,
        maintenance_id: UUID,
        data: MaintenanceComplete,
        current_user: User = None
    ) -> Maintenance:
        """
        Complete a maintenance record.

        Business Rules:
        - Maintenance must be In Progress
        - Completed date cannot be before scheduled date
        - Actual cost cannot be negative (enforced by schema)
        - Sets vehicle.status back to 'Available'

        Raises:
            NotFoundError: If not found
            BusinessLogicError: If business rules violated
        """
        record = self.get_maintenance(maintenance_id)

        if not record.can_be_completed:
            raise BusinessLogicError(
                f"Cannot complete maintenance '{record.maintenance_number}' "
                f"with status '{record.status}'. "
                "Only 'In Progress' maintenance can be completed.",
                code="BIZ_024"
            )

        # Validate completed date is not before scheduled date
        if data.completed_date < record.scheduled_date:
            raise BusinessLogicError(
                f"Completed date ({data.completed_date}) cannot be before "
                f"scheduled date ({record.scheduled_date}).",
                code="BIZ_025"
            )

        # Restore vehicle status
        vehicle = self.vehicle_repository.get_by_id(record.vehicle_id)
        if vehicle.status == 'In Shop':
            vehicle.status = 'Available'

        # Update record
        update_data = {
            "status": "Completed",
            "completed_date": data.completed_date,
            "actual_cost": float(data.actual_cost),
        }
        if data.notes is not None:
            update_data["notes"] = data.notes

        completed_record = self.repository.update(record, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.MAINTENANCE,
                activity_type=ActivityTypeEnum.COMPLETED,
                title="Maintenance Completed",
                description=f"Vehicle {vehicle.registration_number} cleared for operation.",
                severity=SeverityEnum.SUCCESS,
                status="Success",
                user_id=current_user.id,
                maintenance_id=completed_record.id,
                vehicle_id=vehicle.id
            ))
            
        return completed_record

    # ============================================================
    # DELETE
    # ============================================================

    def delete_maintenance(self, maintenance_id: UUID, current_user: User = None) -> None:
        """
        Delete a maintenance record.

        Business Rules:
        - Cannot delete In Progress maintenance (complete or cancel first)
        - Cannot delete Completed maintenance (retained for records)

        Raises:
            NotFoundError: If not found
            BusinessLogicError: If business rules violated
        """
        record = self.get_maintenance(maintenance_id)

        # Removed status checks for hackathon to allow deletion

        
        m_num = record.maintenance_number
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.MAINTENANCE,
                activity_type=ActivityTypeEnum.DELETED,
                title=f"Maintenance {m_num} deleted",
                description="Maintenance record removed.",
                severity=SeverityEnum.WARNING,
                status="Success",
                user_id=current_user.id
            ))
            
        self.repository.delete(record)

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_statistics(self) -> dict:
        """Get maintenance statistics by status."""
        return self.repository.count_by_status()

    # ============================================================
    # SCHEDULER
    # ============================================================

    def _map_scheduler_status(self, record: Maintenance) -> str:
        if record.status in ['Pending', 'Approved']:
            if record.scheduled_date < date.today():
                return 'Overdue'
            return 'Scheduled'
        if record.status == 'Rejected':
            return 'Cancelled'
        return record.status

    def _get_status_color(self, status: str) -> str:
        colors = {
            'Scheduled': 'Blue',
            'In Progress': 'Yellow',
            'Completed': 'Green',
            'Overdue': 'Red',
            'Cancelled': 'Gray'
        }
        return colors.get(status, 'Gray')

    def _format_calendar_event(self, record: Maintenance) -> CalendarEventResponse:
        status = self._map_scheduler_status(record)
        return CalendarEventResponse(
            id=record.id,
            title=f"[{record.maintenance_number}] {record.maintenance_type}",
            description=record.description,
            vehicle_id=record.vehicle_id,
            vehicle_name=record.vehicle.vehicle_name if record.vehicle else "Unknown",
            technician_name=record.assigned_technician,
            maintenance_type=record.maintenance_type,
            priority=record.priority,
            status=status,
            scheduled_date=record.scheduled_date,
            start_time=record.start_time,
            end_time=record.end_time,
            estimated_duration=record.estimated_duration,
            color=self._get_status_color(status),
            created_at=record.created_at,
            updated_at=record.updated_at
        )

    def get_scheduler_events(
        self,
        current_user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        technician: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[CalendarEventResponse]:
        """Get calendar events for scheduler with RBAC."""
        
        # RBAC: Technicians only see their assigned maintenance
        if current_user.role.name not in ["Super Admin", "Administrator", "System Admin", "Fleet Manager", "Support Agent"]:
            # Fallback for technicians/drivers to only see their assignments
            tech_name = f"{current_user.first_name} {current_user.last_name}"
            technician = tech_name

        records = self.repository.get_scheduler_events(
            start_date=start_date,
            end_date=end_date,
            status=status,
            priority=priority,
            vehicle_id=vehicle_id,
            technician=technician,
            search=search
        )
        return [self._format_calendar_event(r) for r in records]

    def reschedule_event(
        self,
        maintenance_id: UUID,
        data: MaintenanceReschedule,
        current_user: User
    ) -> CalendarEventResponse:
        """Reschedule a maintenance event."""
        record = self.get_maintenance(maintenance_id)
        
        if record.status in ['Completed', 'Rejected']:
            raise BusinessLogicError(
                f"Cannot reschedule '{record.status}' maintenance.",
                code="BIZ_028"
            )

        update_data = data.model_dump(exclude_unset=True)
        updated_record = self.repository.update(record, update_data)
        
        activity_service.log_activity(self.db, ActivityCreate(
            module=ModuleEnum.MAINTENANCE,
            activity_type=ActivityTypeEnum.UPDATED,
            title="Maintenance Rescheduled",
            description=f"Maintenance {record.maintenance_number} rescheduled to {data.scheduled_date}.",
            severity=SeverityEnum.INFO,
            status="Success",
            user_id=current_user.id,
            maintenance_id=updated_record.id,
            vehicle_id=updated_record.vehicle_id
        ))
        
        return self._format_calendar_event(updated_record)
