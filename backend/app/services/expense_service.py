"""
Expense service layer containing business logic.
"""
from datetime import date, timezone, datetime
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseStatusUpdate
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.utils.exceptions import (
    NotFoundError,
    BusinessLogicError,
)
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User


class ExpenseService:
    """Service for expense business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ExpenseRepository(db)
        self.vehicle_repository = VehicleRepository(db)
        self.trip_repository = TripRepository(db)
        self.maintenance_repository = MaintenanceRepository(db)

    # ============================================================
    # READ
    # ============================================================

    def get_expense(self, expense_id: UUID) -> Expense:
        """
        Get expense record by ID.

        Raises:
            NotFoundError: If record not found
        """
        record = self.repository.get_by_id(expense_id)
        if not record:
            raise NotFoundError(
                f"Expense record with ID {expense_id} not found"
            )
        return record

    def get_expenses(
        self,
        page: int = 1,
        page_size: int = 20,
        expense_type: str | None = None,
        vehicle_id: UUID | None = None,
        trip_id: UUID | None = None,
        status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search: str | None = None
    ) -> Tuple[List[Expense], int]:
        """
        Get all expense records with pagination and filters.

        Returns:
            Tuple of (records list, total count)
        """
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            expense_type=expense_type,
            vehicle_id=vehicle_id,
            trip_id=trip_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            search=search
        )

    # ============================================================
    # VALIDATION HELPERS
    # ============================================================

    def _validate_relations(self, vehicle_id: Optional[UUID], trip_id: Optional[UUID], maintenance_id: Optional[UUID]):
        """Validate that related entities exist if their IDs are provided."""
        
        # 1. At least one relation must exist
        if not any([vehicle_id, trip_id, maintenance_id]):
            raise BusinessLogicError(
                "An expense must be related to at least one entity (Vehicle, Trip, or Maintenance).",
                code="BIZ_040"
            )

        # 2. Check existence of provided relations
        if vehicle_id:
            vehicle = self.vehicle_repository.get_by_id(vehicle_id)
            if not vehicle:
                raise NotFoundError(f"Vehicle with ID {vehicle_id} not found")
                
        if trip_id:
            trip = self.trip_repository.get_by_id(trip_id)
            if not trip:
                raise NotFoundError(f"Trip with ID {trip_id} not found")
                
            # If both trip and vehicle provided, ensure trip belongs to vehicle
            if vehicle_id and trip.vehicle_id != vehicle_id:
                raise BusinessLogicError(
                    f"Trip '{trip.trip_number}' belongs to a different vehicle.",
                    code="BIZ_041"
                )

        if maintenance_id:
            maintenance = self.maintenance_repository.get_by_id(maintenance_id)
            if not maintenance:
                raise NotFoundError(f"Maintenance record with ID {maintenance_id} not found")
                
            # If both maintenance and vehicle provided, ensure maintenance belongs to vehicle
            if vehicle_id and maintenance.vehicle_id != vehicle_id:
                raise BusinessLogicError(
                    f"Maintenance record '{maintenance.maintenance_number}' belongs to a different vehicle.",
                    code="BIZ_042"
                )

    # ============================================================
    # CREATE
    # ============================================================

    def create_expense(
        self,
        data: ExpenseCreate,
        recorded_by: UUID
    ) -> Expense:
        """
        Create a new expense record.

        Business Rules:
        - At least one of vehicle_id, trip_id, or maintenance_id should be set
        - All referenced entities must exist
        - Expense date cannot be in the future
        - Amount must be > 0 (enforced by schema)

        Raises:
            NotFoundError: If related entity not found
            BusinessLogicError: If business rules violated
        """
        # 1. Validate date
        if data.expense_date > date.today():
            raise BusinessLogicError(
                "Expense date cannot be in the future.",
                code="BIZ_043"
            )

        # 2. Validate relations
        self._validate_relations(data.vehicle_id, data.trip_id, data.maintenance_id)

        # Build data dict
        record_dict = data.model_dump()
        record_dict["status"] = "Pending"
        record_dict["recorded_by"] = recorded_by

        record = self.repository.create(record_dict)
        
        if recorded_by:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.EXPENSE,
                activity_type=ActivityTypeEnum.CREATED,
                title="Expense Logged",
                description=f"New expense of ${data.amount} for {data.expense_type}.",
                severity=SeverityEnum.INFO,
                status="Pending",
                user_id=recorded_by,
                vehicle_id=data.vehicle_id,
                trip_id=data.trip_id
            ))
            
        return record

    # ============================================================
    # UPDATE
    # ============================================================

    def update_expense(
        self,
        expense_id: UUID,
        data: ExpenseUpdate,
        current_user: User = None
    ) -> Expense:
        """
        Update an expense record.

        Business Rules:
        - Cannot update approved expenses
        - Validates date
        - Validates relations
        """
        record = self.get_expense(expense_id)

        if record.status == 'Approved':
            raise BusinessLogicError(
                "Cannot update an approved expense.",
                code="BIZ_044"
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate date if provided
        if "expense_date" in update_data and update_data["expense_date"] > date.today():
            raise BusinessLogicError(
                "Expense date cannot be in the future.",
                code="BIZ_043"
            )

        # Re-validate relations if any ID changed
        if any(k in update_data for k in ["vehicle_id", "trip_id", "maintenance_id"]):
            v_id = update_data.get("vehicle_id", record.vehicle_id)
            t_id = update_data.get("trip_id", record.trip_id)
            m_id = update_data.get("maintenance_id", record.maintenance_id)
            self._validate_relations(v_id, t_id, m_id)

        updated_record = self.repository.update(record, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.EXPENSE,
                activity_type=ActivityTypeEnum.UPDATED,
                title="Expense Updated",
                description="Expense parameters were modified.",
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id,
                vehicle_id=updated_record.vehicle_id,
                trip_id=updated_record.trip_id
            ))
            
        return updated_record

    # ============================================================
    # LIFECYCLE (Approve/Reject)
    # ============================================================

    def approve_expense(self, expense_id: UUID, approved_by: UUID) -> Expense:
        """Approve a pending expense."""
        record = self.get_expense(expense_id)
        
        if record.status == 'Approved':
            raise BusinessLogicError("Expense is already approved.")
            
        update_data = {
            "status": "Approved",
            "approved_by": approved_by
        }
        updated_record = self.repository.update(record, update_data)
        
        if approved_by:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.EXPENSE,
                activity_type=ActivityTypeEnum.APPROVED,
                title="Expense Approved",
                description=f"Expense of ${updated_record.amount} was approved.",
                severity=SeverityEnum.SUCCESS,
                status="Success",
                user_id=approved_by,
                vehicle_id=updated_record.vehicle_id,
                trip_id=updated_record.trip_id
            ))
            
        return updated_record

    def reject_expense(self, expense_id: UUID, data: ExpenseStatusUpdate, current_user: User = None) -> Expense:
        """Reject a pending expense."""
        record = self.get_expense(expense_id)
        
        if record.status == 'Approved':
            raise BusinessLogicError("Cannot reject an already approved expense.")
            
        # Optional: could store the reason in `description` or `vendor_name` if no explicit field exists. 
        # But schema has no `reason` field in DB. We just change status.
        
        update_data = {
            "status": "Rejected"
        }
        updated_record = self.repository.update(record, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.EXPENSE,
                activity_type=ActivityTypeEnum.REJECTED,
                title="Expense Rejected",
                description=f"Expense of ${updated_record.amount} was rejected.",
                severity=SeverityEnum.WARNING,
                status="Success",
                user_id=current_user.id,
                vehicle_id=updated_record.vehicle_id,
                trip_id=updated_record.trip_id
            ))
            
        return updated_record

    # ============================================================
    # DELETE
    # ============================================================

    def delete_expense(self, expense_id: UUID, current_user: User = None) -> None:
        """
        Delete an expense record.
        
        Business Rules:
        - Approved expenses cannot be deleted.
        """
        record = self.get_expense(expense_id)
        
        if record.status == 'Approved':
            raise BusinessLogicError(
                "Approved expenses cannot be deleted.",
                code="BIZ_045"
            )
            
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.EXPENSE,
                activity_type=ActivityTypeEnum.DELETED,
                title="Expense Deleted",
                description="Expense record was removed.",
                severity=SeverityEnum.WARNING,
                status="Success",
                user_id=current_user.id
            ))
            
        self.repository.delete(record)
