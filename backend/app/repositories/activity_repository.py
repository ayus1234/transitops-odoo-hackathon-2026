from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func, and_, cast, String
from typing import Tuple, List, Dict, Any, Optional
from datetime import datetime, date

from app.models.activity import ActivityLog, ModuleEnum, SeverityEnum
from app.schemas.activity import ActivityCreate, ActivityFilterRequest

class ActivityRepository:
    def get(self, db: Session, id: Any) -> Optional[ActivityLog]:
        return db.query(ActivityLog).filter(ActivityLog.id == id).first()

    def log_activity(self, db: Session, *, activity_in: ActivityCreate) -> ActivityLog:
        db_obj = ActivityLog(
            **activity_in.model_dump(exclude_unset=True, by_alias=True)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_activities(
        self, 
        db: Session, 
        *, 
        filters: ActivityFilterRequest, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[ActivityLog], int]:
        
        query = db.query(ActivityLog)
        
        if filters:
            if filters.module:
                query = query.filter(ActivityLog.module == filters.module)
            if filters.activity_type:
                query = query.filter(ActivityLog.activity_type == filters.activity_type)
            if filters.severity:
                query = query.filter(ActivityLog.severity == filters.severity)
            if filters.status:
                query = query.filter(ActivityLog.status == filters.status)
            
            # IDs
            if filters.user_id:
                query = query.filter(ActivityLog.user_id == filters.user_id)
            if filters.vehicle_id:
                query = query.filter(ActivityLog.vehicle_id == filters.vehicle_id)
            if filters.driver_id:
                query = query.filter(ActivityLog.driver_id == filters.driver_id)
            if filters.trip_id:
                query = query.filter(ActivityLog.trip_id == filters.trip_id)
                
            # Dates
            if filters.start_date:
                query = query.filter(ActivityLog.created_at >= filters.start_date)
            if filters.end_date:
                query = query.filter(ActivityLog.created_at <= filters.end_date)
                
            # Search
            if filters.query:
                search_term = f"%{filters.query}%"
                query = query.filter(
                    or_(
                        ActivityLog.title.ilike(search_term),
                        ActivityLog.description.ilike(search_term),
                        cast(ActivityLog.id, String).ilike(search_term),
                        cast(ActivityLog.user_id, String).ilike(search_term),
                        cast(ActivityLog.vehicle_id, String).ilike(search_term),
                        cast(ActivityLog.driver_id, String).ilike(search_term)
                    )
                )

        # Order by newest first
        query = query.order_by(desc(ActivityLog.created_at))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        
        return items, total

    def get_statistics(self, db: Session, user_id: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculates global or scoped statistics based on role/user_id.
        Since statistics requirements didn't specify per-user stats explicitly but it's good practice.
        """
        query = db.query(ActivityLog)
        
        if role == "driver" and user_id:
            query = query.filter(ActivityLog.user_id == user_id)
            
        today_start = datetime.combine(date.today(), datetime.min.time())
        
        total_activities = query.count()
        today_activities = query.filter(ActivityLog.created_at >= today_start).count()
        critical_activities = query.filter(ActivityLog.severity == SeverityEnum.CRITICAL).count()
        warnings = query.filter(ActivityLog.severity == SeverityEnum.WARNING).count()
        successful_actions = query.filter(ActivityLog.status.ilike('success')).count()
        failed_actions = query.filter(ActivityLog.status.ilike('failed')).count()
        
        # Group by module
        module_counts = db.query(ActivityLog.module, func.count(ActivityLog.id)).group_by(ActivityLog.module).all()
        activities_by_module = {mod.value: count for mod, count in module_counts}
        
        # Group by severity
        severity_counts = db.query(ActivityLog.severity, func.count(ActivityLog.id)).group_by(ActivityLog.severity).all()
        activities_by_severity = {sev.value: count for sev, count in severity_counts}
        
        return {
            "total_activities": total_activities,
            "today_activities": today_activities,
            "critical_activities": critical_activities,
            "warnings": warnings,
            "successful_actions": successful_actions,
            "failed_actions": failed_actions,
            "activities_by_module": activities_by_module,
            "activities_by_severity": activities_by_severity
        }

activity_repository = ActivityRepository()
