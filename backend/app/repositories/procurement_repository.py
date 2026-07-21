from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.inventory import ProcurementRequest, ProcurementStatusEnum
from app.schemas.inventory import ProcurementRequestCreate, ProcurementRequestUpdate
from app.models.user import User

class ProcurementRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, req_id: UUID) -> Optional[ProcurementRequest]:
        return self.db.query(ProcurementRequest).filter(ProcurementRequest.id == req_id).first()

    def get_by_procurement_id(self, procurement_id: str) -> Optional[ProcurementRequest]:
        return self.db.query(ProcurementRequest).filter(ProcurementRequest.procurement_id == procurement_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ProcurementRequest], int]:
        query = self.db.query(ProcurementRequest)

        if status:
            query = query.filter(ProcurementRequest.status == status)

        if search:
            search_filter = or_(
                ProcurementRequest.procurement_id.ilike(f"%{search}%"),
                ProcurementRequest.vendor.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        total = query.count()
        reqs = query.order_by(ProcurementRequest.created_at.desc()).offset(skip).limit(limit).all()

        return reqs, total

    def create(self, data: ProcurementRequestCreate, procurement_id: str, requested_by_id: UUID) -> ProcurementRequest:
        req = ProcurementRequest(
            **data.model_dump(),
            procurement_id=procurement_id,
            requested_by_id=requested_by_id
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def update(self, req: ProcurementRequest, data: ProcurementRequestUpdate) -> ProcurementRequest:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(req, field, value)
        
        self.db.commit()
        self.db.refresh(req)
        return req

    def delete(self, req: ProcurementRequest) -> None:
        self.db.delete(req)
        self.db.commit()

    def count_by_status(self) -> dict:
        result = self.db.query(
            ProcurementRequest.status,
            func.count(ProcurementRequest.id).label('count')
        ).group_by(ProcurementRequest.status).all()
        return {status: count for status, count in result}
    
    def generate_procurement_id(self) -> str:
        count = self.db.query(ProcurementRequest).count()
        return f"PR-{2026}-{count+1:04d}"
