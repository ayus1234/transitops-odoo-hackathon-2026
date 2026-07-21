from typing import List, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem, InventoryHistoryTypeEnum, PartStatusEnum
from app.schemas.inventory import (
    InventoryItemCreate, 
    InventoryItemUpdate, 
    InventoryDashboardSummary,
    InventoryHistoryCreate
)
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.inventory_history_repository import InventoryHistoryRepository
from app.repositories.procurement_repository import ProcurementRepository
from app.repositories.purchase_order_repository import PurchaseOrderRepository

from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.services.activity_service import activity_service
from app.services.notification_service import NotificationService
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User

class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = InventoryRepository(db)
        self.history_repo = InventoryHistoryRepository(db)
        self.procurement_repo = ProcurementRepository(db)
        self.po_repo = PurchaseOrderRepository(db)

    def get_dashboard_summary(self) -> InventoryDashboardSummary:
        items, _ = self.repository.get_all(limit=10000)
        
        total_parts = len(items)
        available_parts = sum(1 for item in items if item.quantity_available > 0)
        
        low_stock_parts = len(self.repository.get_low_stock_items())
        critical_alerts = len(self.repository.get_critical_stock_items())
        out_of_stock = len(self.repository.get_out_of_stock_items())
        
        # Vehicles Waiting: simplified logic - count active maintenance tasks with "Pending" status
        from app.models.maintenance import Maintenance
        vehicles_waiting = self.db.query(Maintenance).filter(Maintenance.status == 'Pending').count()
        estimated_downtime = vehicles_waiting * 24.0 # 24 hours per vehicle waiting
        
        reqs, _ = self.procurement_repo.get_all(limit=10000)
        pending_requests = sum(1 for r in reqs if r.status in ["Submitted", "Approved"])
        
        pos, _ = self.po_repo.get_all(limit=10000)
        pending_pos = sum(1 for po in pos if po.shipment_status not in ["Delivered", "Cancelled"])
        
        # Health Score: 100 - (percentage of critical + out of stock)
        health_score = 100.0
        if total_parts > 0:
            penalty = ((critical_alerts + out_of_stock) / total_parts) * 100
            health_score = max(0.0, 100.0 - penalty)

        return InventoryDashboardSummary(
            total_parts=total_parts,
            available_parts=available_parts,
            low_stock_parts=low_stock_parts,
            critical_stock_alerts=critical_alerts,
            out_of_stock_parts=out_of_stock,
            vehicles_waiting=vehicles_waiting,
            estimated_downtime_hours=estimated_downtime,
            pending_procurement_requests=pending_requests,
            pending_purchase_orders=pending_pos,
            inventory_health_score=round(health_score, 1)
        )

    def update_stock(
        self, 
        part_id: UUID, 
        quantity_change: int, 
        type: InventoryHistoryTypeEnum,
        user_id: UUID,
        reference_id: str = None,
        vendor: str = None,
        cost: float = None
    ) -> InventoryItem:
        item = self.repository.get_by_id(part_id)
        if not item:
            raise NotFoundError("Part not found")

        prev_qty = item.quantity_available
        new_qty = prev_qty + quantity_change
        
        if new_qty < 0:
            raise BusinessLogicError(f"Insufficient stock for {item.name}. Available: {prev_qty}")

        # Update item
        item.quantity_available = new_qty
        
        # Update status based on levels
        if new_qty == 0:
            item.status = PartStatusEnum.OUT_OF_STOCK
        elif new_qty <= item.critical_stock_level:
            item.status = PartStatusEnum.CRITICAL_STOCK
        elif new_qty <= item.minimum_stock_level:
            item.status = PartStatusEnum.LOW_STOCK
        else:
            item.status = PartStatusEnum.IN_STOCK
            
        self.db.commit()

        # Record history
        self.history_repo.create(InventoryHistoryCreate(
            part_id=item.id,
            type=type,
            quantity_changed=quantity_change,
            previous_quantity=prev_qty,
            new_quantity=new_qty,
            user_id=user_id,
            reference_id=reference_id,
            vendor=vendor,
            cost=cost
        ))
        
        # Check alerts
        if item.status == PartStatusEnum.CRITICAL_STOCK:
            NotificationService.notify_user(
                self.db, user_id, 
                title="Critical Stock Alert", 
                description=f"Part {item.name} is critically low ({new_qty} remaining).",
                type="Alert", module_name="Inventory", severity="Critical"
            )

        return item
