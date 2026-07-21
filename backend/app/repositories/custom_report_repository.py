from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from uuid import UUID

from app.models.custom_report import CustomReport, ReportExecution, ScheduledReport
from app.schemas.custom_report import CustomReportCreate, CustomReportUpdate

class CustomReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, report_in: CustomReportCreate, user_id: UUID) -> CustomReport:
        db_obj = CustomReport(
            **report_in.model_dump(),
            created_by=user_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get(self, report_id: UUID) -> Optional[CustomReport]:
        return self.db.query(CustomReport).filter(CustomReport.id == report_id).first()

    def get_multi(self, user_id: UUID, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Tuple[List[CustomReport], int]:
        query = self.db.query(CustomReport).filter(
            or_(
                CustomReport.created_by == user_id,
                CustomReport.is_public == True
            )
        )
        
        if search:
            query = query.filter(CustomReport.name.ilike(f"%{search}%"))
            
        total = query.count()
        reports = query.order_by(desc(CustomReport.created_at)).offset(skip).limit(limit).all()
        return reports, total

    def update(self, db_obj: CustomReport, report_in: CustomReportUpdate) -> CustomReport:
        update_data = report_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: CustomReport) -> None:
        self.db.delete(db_obj)
        self.db.commit()

class ReportExecutionRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, report_id: UUID, user_id: UUID, duration_ms: int, status: str, row_count: int, file_path: Optional[str] = None) -> ReportExecution:
        db_obj = ReportExecution(
            report_id=report_id,
            executed_by=user_id,
            duration_ms=duration_ms,
            status=status,
            row_count=row_count,
            file_path=file_path
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
        
    def get_by_report(self, report_id: UUID, skip: int = 0, limit: int = 50) -> List[ReportExecution]:
        return self.db.query(ReportExecution).filter(
            ReportExecution.report_id == report_id
        ).order_by(desc(ReportExecution.execution_time)).offset(skip).limit(limit).all()
        
    def count_total(self) -> int:
        return self.db.query(ReportExecution).count()

class ScheduledReportRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_report(self, report_id: UUID) -> Optional[ScheduledReport]:
        return self.db.query(ScheduledReport).filter(ScheduledReport.report_id == report_id).first()
