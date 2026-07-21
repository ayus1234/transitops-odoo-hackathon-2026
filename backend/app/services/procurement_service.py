from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.inventory import ProcurementRequest, ProcurementStatusEnum
from app.schemas.inventory import ProcurementRequestCreate, ProcurementRequestUpdate, ProcurementSummary
from app.schemas.activity import ActivityCreate
from app.repositories.procurement_repository import ProcurementRepository
from app.repositories.inventory_repository import InventoryRepository

from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.services.activity_service import activity_service
from app.services.notification_service import NotificationService
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User

class ProcurementService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProcurementRepository(db)
        self.inventory_repo = InventoryRepository(db)

    def get_summary(self) -> ProcurementSummary:
        counts = self.repository.count_by_status()
        total = sum(counts.values())
        return ProcurementSummary(
            total_requests=total,
            draft_requests=counts.get(ProcurementStatusEnum.DRAFT.value, 0),
            submitted_requests=counts.get(ProcurementStatusEnum.SUBMITTED.value, 0),
            approved_requests=counts.get(ProcurementStatusEnum.APPROVED.value, 0),
            rejected_requests=counts.get(ProcurementStatusEnum.REJECTED.value, 0),
            ordered_requests=counts.get(ProcurementStatusEnum.ORDERED.value, 0),
            delivered_requests=counts.get(ProcurementStatusEnum.DELIVERED.value, 0)
        )

    def create_request(self, data: ProcurementRequestCreate, current_user: User) -> ProcurementRequest:
        part = self.inventory_repo.get_by_id(data.part_id)
        if not part:
            raise NotFoundError("Part not found")

        pr_id = self.repository.generate_procurement_id()
        req = self.repository.create(data, pr_id, current_user.id)
        
        # Auto-submit if not draft
        req.status = ProcurementStatusEnum.SUBMITTED
        self.db.commit()
        
        activity_service.log_activity(
            self.db,
            activity_in=ActivityCreate(
                title="Procurement Request Created",
                description=f"Request {pr_id} created for {data.required_quantity}x {part.name}",
                module=ModuleEnum.PROCUREMENT,
                activity_type=ActivityTypeEnum.CREATED,
                user_id=current_user.id,
                severity=SeverityEnum.INFO
            )
        )
        
        NotificationService.notify_user(
            self.db, current_user.id,
            title="Request Submitted",
            description=f"Procurement request {pr_id} submitted successfully.",
            type="Info", module_name="Procurement"
        )
        
        return req

    def approve_request(self, req_id: UUID, current_user: User) -> ProcurementRequest:
        req = self.repository.get_by_id(req_id)
        if not req:
            raise NotFoundError("Request not found")
            
        if req.status != ProcurementStatusEnum.SUBMITTED:
            raise BusinessLogicError("Only submitted requests can be approved")
            
        req.status = ProcurementStatusEnum.APPROVED
        req.approved_by_id = current_user.id
        self.db.commit()
        
        activity_service.log_activity(
            self.db,
            activity_in=ActivityCreate(
                title="Procurement Request Approved",
                description=f"Request {req.procurement_id} approved by {current_user.full_name}",
                module=ModuleEnum.PROCUREMENT,
                activity_type=ActivityTypeEnum.APPROVED,
                user_id=current_user.id,
                severity=SeverityEnum.SUCCESS
            )
        )
        
        return req

    def reject_request(self, req_id: UUID, current_user: User) -> ProcurementRequest:
        req = self.repository.get_by_id(req_id)
        if not req:
            raise NotFoundError("Request not found")
            
        if req.status != ProcurementStatusEnum.SUBMITTED:
            raise BusinessLogicError("Only submitted requests can be rejected")
            
        req.status = ProcurementStatusEnum.REJECTED
        self.db.commit()
        
        activity_service.log_activity(
            self.db,
            activity_in=ActivityCreate(
                title="Procurement Request Rejected",
                description=f"Request {req.procurement_id} rejected by {current_user.full_name}",
                module=ModuleEnum.PROCUREMENT,
                activity_type=ActivityTypeEnum.CANCELLED,
                user_id=current_user.id,
                severity=SeverityEnum.WARNING
            )
        )
        
        return req
