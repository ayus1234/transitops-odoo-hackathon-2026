"""
Pydantic schemas for the Quick Actions module.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class QuickActionBase(BaseModel):
    name: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    category: str = Field(..., max_length=50)
    route: str = Field(..., max_length=255)
    http_method: Optional[str] = Field("GET", max_length=20)
    permission_resource: str = Field(..., max_length=100)
    permission_action: str = Field(..., max_length=50)
    display_order: int = 0
    color: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    is_favorite: bool = False


class QuickActionResponse(QuickActionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # We will override is_favorite dynamically per user in the service layer
    
    model_config = {"from_attributes": True}


class QuickActionListResponse(BaseModel):
    success: bool = True
    data: List[QuickActionResponse]


class QuickActionStatistics(BaseModel):
    total_actions: int
    active_actions: int
    favorites_count: int
    recent_actions_count: int


class FavoriteActionRequest(BaseModel):
    is_favorite: bool


class RecentActionResponse(BaseModel):
    id: UUID
    action_id: UUID
    last_accessed_at: datetime
    access_count: int
    action: QuickActionResponse
    
    model_config = {"from_attributes": True}


class ExecuteActionResponse(BaseModel):
    action: QuickActionResponse
    target_route: str
    http_method: str
    required_permission: dict

class FavoriteActionAddRequest(BaseModel):
    action_id: UUID

class FavoriteActionRemoveRequest(BaseModel):
    action_id: UUID

class PermissionsResponse(BaseModel):
    allowed: List[QuickActionResponse]
    restricted: List[QuickActionResponse]
