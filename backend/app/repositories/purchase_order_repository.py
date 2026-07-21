from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.inventory import PurchaseOrder, ShipmentStatusEnum
from app.schemas.inventory import PurchaseOrderCreate, PurchaseOrderUpdate

class PurchaseOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, po_id: UUID) -> Optional[PurchaseOrder]:
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()

    def get_by_po_number(self, po_number: str) -> Optional[PurchaseOrder]:
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[PurchaseOrder], int]:
        query = self.db.query(PurchaseOrder)

        if status:
            query = query.filter(PurchaseOrder.shipment_status == status)

        if search:
            search_filter = or_(
                PurchaseOrder.po_number.ilike(f"%{search}%"),
                PurchaseOrder.vendor_name.ilike(f"%{search}%"),
                PurchaseOrder.tracking_id.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        total = query.count()
        orders = query.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit).all()

        return orders, total

    def create(self, data: PurchaseOrderCreate, po_number: str) -> PurchaseOrder:
        order = PurchaseOrder(
            **data.model_dump(),
            po_number=po_number
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order: PurchaseOrder, data: PurchaseOrderUpdate) -> PurchaseOrder:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def count_by_status(self) -> dict:
        result = self.db.query(
            PurchaseOrder.shipment_status,
            func.count(PurchaseOrder.id).label('count')
        ).group_by(PurchaseOrder.shipment_status).all()
        return {status: count for status, count in result}
    
    def generate_po_number(self) -> str:
        count = self.db.query(PurchaseOrder).count()
        return f"PO-{2026}-{count+1:04d}"
