from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum

class ActivityBase(BaseModel):
    module: ModuleEnum
    activity_type: ActivityTypeEnum
    title: str
    description: Optional[str] = None
    severity: SeverityEnum = SeverityEnum.INFO
    status: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    # FKs
    user_id: Optional[UUID4] = None
    vehicle_id: Optional[UUID4] = None
    driver_id: Optional[UUID4] = None
    trip_id: Optional[UUID4] = None
    maintenance_id: Optional[UUID4] = None
    fuel_id: Optional[UUID4] = None
    expense_id: Optional[UUID4] = None

class ActivityCreate(ActivityBase):
    pass

class ActivityResponse(ActivityBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class ActivityListResponse(BaseModel):
    items: List[ActivityResponse]
    total: int
    page: int
    size: int
    pages: int

class ActivityFilterRequest(BaseModel):
    module: Optional[ModuleEnum] = None
    activity_type: Optional[ActivityTypeEnum] = None
    severity: Optional[SeverityEnum] = None
    status: Optional[str] = None
    
    # Specific ID filters
    user_id: Optional[UUID4] = None
    vehicle_id: Optional[UUID4] = None
    driver_id: Optional[UUID4] = None
    trip_id: Optional[UUID4] = None
    
    # Date ranges
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Search
    query: Optional[str] = None

class ActivityStatisticsResponse(BaseModel):
    total_activities: int
    today_activities: int
    critical_activities: int
    warnings: int
    successful_actions: int
    failed_actions: int
    activities_by_module: Dict[str, int]
    activities_by_severity: Dict[str, int]

class ExportActivityRequest(BaseModel):
    filters: Optional[ActivityFilterRequest] = None
    format: str = Field(default="csv", description="csv or pdf")
