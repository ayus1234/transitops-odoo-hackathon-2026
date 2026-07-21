from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import UUID4
import math

from app.api.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.schemas.activity import (
    ActivityResponse, 
    ActivityListResponse, 
    ActivityFilterRequest, 
    ActivityStatisticsResponse,
    ActivityCreate
)
from app.services.activity_service import activity_service
from app.repositories.activity_repository import activity_repository

router = APIRouter()

@router.get("", response_model=ActivityListResponse)
def get_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=10000),
    module: Optional[ModuleEnum] = None,
    activity_type: Optional[ActivityTypeEnum] = None,
    severity: Optional[SeverityEnum] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID4] = None,
    vehicle_id: Optional[UUID4] = None,
    driver_id: Optional[UUID4] = None,
    trip_id: Optional[UUID4] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
):
    """
    Get paginated activity logs with optional filtering.
    """
    filters = ActivityFilterRequest(
        module=module,
        activity_type=activity_type,
        severity=severity,
        status=status,
        user_id=user_id,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        trip_id=trip_id,
        start_date=start_date,
        end_date=end_date,
        query=search
    )
    
    items, total = activity_service.get_activities(
        db, current_user=current_user, filters=filters, skip=skip, limit=limit
    )
    
    pages = math.ceil(total / limit) if total > 0 else 0
    
    return ActivityListResponse(
        items=items,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=pages
    )

@router.get("/statistics", response_model=ActivityStatisticsResponse)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get high-level activity statistics.
    """
    stats = activity_service.get_statistics(db, current_user=current_user)
    return ActivityStatisticsResponse(**stats)

@router.get("/export")
def export_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    format: str = Query("csv", pattern="^(csv|pdf)$"),
    module: Optional[ModuleEnum] = None,
    activity_type: Optional[ActivityTypeEnum] = None,
    severity: Optional[SeverityEnum] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID4] = None,
    vehicle_id: Optional[UUID4] = None,
    driver_id: Optional[UUID4] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
):
    """
    Export activities as CSV or PDF based on applied filters.
    """
    filters = ActivityFilterRequest(
        module=module,
        activity_type=activity_type,
        severity=severity,
        status=status,
        user_id=user_id,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        start_date=start_date,
        end_date=end_date,
        query=search
    )
    
    if format == "csv":
        csv_data = activity_service.export_csv(db, current_user, filters)
        return Response(
            content=csv_data, 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename=activity_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"}
        )
    else:
        pdf_data = activity_service.export_pdf(db, current_user, filters)
        return Response(
            content=pdf_data, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=activity_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"}
        )

@router.get("/recent", response_model=List[ActivityResponse])
def get_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(5, ge=1, le=50)
):
    """
    Get the most recent activities for the dashboard widget.
    """
    filters = ActivityFilterRequest()
    items, _ = activity_service.get_activities(
        db, current_user=current_user, filters=filters, skip=0, limit=limit
    )
    return items

@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity_by_id(
    activity_id: UUID4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific activity details.
    """
    activity = activity_repository.get(db, id=activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    # Note: To be extremely strict we could re-run the RBAC validation here.
    # For now, if they can hit the endpoint, they're good, but typically Drivers only see their own.
    role_name = current_user.role.name.lower() if current_user.role is not None else ""
    if role_name == "driver" and str(activity.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this activity")
        
    return activity

@router.post("", response_model=ActivityResponse, dependencies=[Depends(RoleChecker(["Administrator"]))])
def create_manual_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually create an activity (restricted to internal system/admin use).
    """
    # Force user_id to current_user if not specified
    if not activity_in.user_id:
        activity_in.user_id = current_user.id # type: ignore
        
    return activity_service.log_activity(db, activity_in)
