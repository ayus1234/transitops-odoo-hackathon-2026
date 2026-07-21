from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.inventory import InventoryHistory, InventoryItem
from app.schemas.inventory import InventoryHistoryCreate

class InventoryHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        part_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> Tuple[List[InventoryHistory], int]:
        query = self.db.query(InventoryHistory)

        if part_id:
            query = query.filter(InventoryHistory.part_id == part_id)

        if search:
            # Join with InventoryItem to search by part name or part number
            query = query.join(InventoryItem)
            search_filter = or_(
                InventoryHistory.vendor.ilike(f"%{search}%"),
                InventoryHistory.reference_id.ilike(f"%{search}%"),
                InventoryItem.name.ilike(f"%{search}%"),
                InventoryItem.part_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        total = query.count()
        logs = query.order_by(InventoryHistory.created_at.desc()).offset(skip).limit(limit).all()

        return logs, total

    def create(self, data: InventoryHistoryCreate) -> InventoryHistory:
        log = InventoryHistory(**data.model_dump())
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
