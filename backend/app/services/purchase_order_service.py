from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.inventory import PurchaseOrder, ShipmentStatusEnum, ProcurementStatusEnum, InventoryHistoryTypeEnum
from app.schemas.inventory import PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderSummary
from app.repositories.purchase_order_repository import PurchaseOrderRepository
from app.repositories.procurement_repository import ProcurementRepository
from app.services.inventory_service import InventoryService

from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.services.activity_service import activity_service
from app.services.notification_service import NotificationService
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.schemas.activity import ActivityCreate
from app.models.user import User

class PurchaseOrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PurchaseOrderRepository(db)
        self.procurement_repo = ProcurementRepository(db)
        self.inventory_service = InventoryService(db)

    def get_summary(self) -> PurchaseOrderSummary:
        counts = self.repository.count_by_status()
        total = sum(counts.values())
        return PurchaseOrderSummary(
            total_orders=total,
            processing=counts.get(ShipmentStatusEnum.PROCESSING.value, 0),
            ordered=counts.get(ShipmentStatusEnum.ORDERED.value, 0),
            dispatched=counts.get(ShipmentStatusEnum.DISPATCHED.value, 0),
            in_transit=counts.get(ShipmentStatusEnum.IN_TRANSIT.value, 0),
            delivered=counts.get(ShipmentStatusEnum.DELIVERED.value, 0),
            delayed=counts.get(ShipmentStatusEnum.DELAYED.value, 0)
        )

    def generate_po_from_request(self, req_id: UUID, current_user: User) -> PurchaseOrder:
        try:
            req = self.procurement_repo.get_by_id(req_id)
            if not req:
                raise NotFoundError("Request not found")
                
            if req.status != ProcurementStatusEnum.APPROVED:
                raise BusinessLogicError("Only approved requests can generate POs")
                
            po_number = self.repository.generate_po_number()
            
            po_data = PurchaseOrderCreate(
                procurement_request_id=req.id,
                vendor_name=req.vendor or "Unknown Vendor",
                quantity=req.required_quantity,
                cost=req.estimated_cost or 0.0
            )
            
            po = self.repository.create(po_data, po_number)
            
            req.status = ProcurementStatusEnum.ORDERED
            self.db.commit()
            
            activity_service.log_activity(
                self.db,
                ActivityCreate(
                    title="Purchase Order Generated",
                    description=f"PO {po_number} generated for PR {req.procurement_id}",
                    module=ModuleEnum.PURCHASE_ORDER,
                    activity_type=ActivityTypeEnum.CREATED,
                    user_id=current_user.id,
                    severity=SeverityEnum.INFO
                )
            )
            
            return po
        except Exception as e:
            import traceback
            raise BusinessLogicError(f"Error generating PO: {str(e)}\n{traceback.format_exc()}")

    def update_shipment_status(self, po_id: UUID, status: ShipmentStatusEnum, current_user: User) -> PurchaseOrder:
        po = self.repository.get_by_id(po_id)
        if not po:
            raise NotFoundError("PO not found")
            
        po.shipment_status = status
        self.db.commit()
        
        # If delivered, update inventory
        if status == ShipmentStatusEnum.DELIVERED:
            req = po.procurement_request
            req.status = ProcurementStatusEnum.DELIVERED
            self.db.commit()
            
            # Update inventory and log history
            self.inventory_service.update_stock(
                part_id=req.part_id,
                quantity_change=po.quantity,
                type=InventoryHistoryTypeEnum.RESTOCK,
                user_id=current_user.id,
                reference_id=po.po_number,
                vendor=po.vendor_name,
                cost=po.cost
            )
            
            NotificationService.notify_user(
                self.db, current_user.id,
                title="Shipment Delivered",
                description=f"PO {po.po_number} delivered. Inventory updated.",
                type="Success", module_name="Purchase Order", severity="Success"
            )
            
        activity_service.log_activity(
            self.db,
            ActivityCreate(
                title="Shipment Status Updated",
                description=f"PO {po.po_number} status changed to {status.value}",
                module=ModuleEnum.PURCHASE_ORDER,
                activity_type=ActivityTypeEnum.UPDATED,
                user_id=current_user.id,
                severity=SeverityEnum.INFO
            )
        )
        
        return po
