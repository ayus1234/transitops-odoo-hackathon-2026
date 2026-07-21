from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem, PartStatusEnum
from app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate

class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, item_id: UUID) -> Optional[InventoryItem]:
        return self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()

    def get_by_part_number(self, part_number: str) -> Optional[InventoryItem]:
        return self.db.query(InventoryItem).filter(InventoryItem.part_number == part_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[InventoryItem], int]:
        query = self.db.query(InventoryItem)

        if status:
            query = query.filter(InventoryItem.status == status)

        if search:
            search_filter = or_(
                InventoryItem.name.ilike(f"%{search}%"),
                InventoryItem.part_number.ilike(f"%{search}%"),
                InventoryItem.vendor.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        total = query.count()
        items = query.order_by(InventoryItem.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def create(self, data: InventoryItemCreate) -> InventoryItem:
        item = InventoryItem(**data.model_dump())
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: InventoryItem, data: InventoryItemUpdate) -> InventoryItem:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: InventoryItem) -> None:
        self.db.delete(item)
        self.db.commit()

    def get_low_stock_items(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).filter(
            InventoryItem.quantity_available <= InventoryItem.minimum_stock_level,
            InventoryItem.quantity_available > InventoryItem.critical_stock_level
        ).all()
        
    def get_critical_stock_items(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).filter(
            InventoryItem.quantity_available <= InventoryItem.critical_stock_level,
            InventoryItem.quantity_available > 0
        ).all()
        
    def get_out_of_stock_items(self) -> List[InventoryItem]:
        return self.db.query(InventoryItem).filter(
            InventoryItem.quantity_available <= 0
        ).all()
        
    def count_by_status(self) -> dict:
        result = self.db.query(
            InventoryItem.status,
            func.count(InventoryItem.id).label('count')
        ).group_by(InventoryItem.status).all()
        return {status: count for status, count in result}
