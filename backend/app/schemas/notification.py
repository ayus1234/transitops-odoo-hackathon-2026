from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    type: str = Field(..., description="Info, Success, Warning, Critical")
    priority: str = Field(..., description="Low, Medium, High, Critical")
    category: str = Field(..., description="Vehicles, Drivers, Trips, Maintenance, Fuel, Expenses, Reports, Settings, Quick Actions, System")
    module_name: str = Field(..., description="Module Name")
    severity: str = Field("Info", description="Severity level")
    icon_name: Optional[str] = None
    route: Optional[str] = Field(None, max_length=255)
    related_entity_id: Optional[UUID] = None
    metadata_payload: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    user_id: UUID


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    is_read: bool
    is_archived: bool
    created_at: datetime
    timestamp: datetime = Field(alias="timestamp", validation_alias="created_at")
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NotificationListResponse(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    data: List[NotificationResponse]


class PriorityStats(BaseModel):
    Low: int = 0
    Medium: int = 0
    High: int = 0
    Critical: int = 0


class TypeStats(BaseModel):
    System: int = 0
    Trip: int = 0
    Maintenance: int = 0
    Fuel: int = 0
    Expense: int = 0
    Vehicle: int = 0
    Driver: int = 0
    Report: int = 0
    Security: int = 0
    Reminder: int = 0
    Other: int = 0


class NotificationStatistics(BaseModel):
    total: int = 0
    unread: int = 0
    read: int = 0
    archived: int = 0
    by_priority: PriorityStats
    by_type: TypeStats
