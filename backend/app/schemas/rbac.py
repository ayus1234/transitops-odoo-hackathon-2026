from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, UUID4
from datetime import datetime

class PermissionMatrix(BaseModel):
    module: str
    permissions: List[str]

class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permissions: Dict[str, List[str]] = Field(default_factory=dict)
    parent_role_id: Optional[UUID4] = None

class RoleCreate(RoleBase):
    is_custom: bool = True

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permissions: Optional[Dict[str, List[str]]] = None
    parent_role_id: Optional[UUID4] = None

class RoleResponse(RoleBase):
    id: UUID4
    is_custom: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleCloneRequest(BaseModel):
    new_name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class UserRoleAssignment(BaseModel):
    user_id: UUID4
    primary_role_id: UUID4
    additional_role_ids: List[UUID4] = Field(default_factory=list)

class PermissionAuditLogResponse(BaseModel):
    id: UUID4
    user_id: Optional[UUID4] = None
    action: str
    module: Optional[str] = None
    target_role_id: Optional[UUID4] = None
    target_user_id: Optional[UUID4] = None
    previous_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Static Permission Templates
TEMPLATES = {
    "Fleet Operations": {
        "vehicles": ["read", "create", "update"],
        "drivers": ["read"],
        "trips": ["read", "create", "update"],
        "dashboard": ["read"],
        "reports": ["read"]
    },
    "Maintenance Operations": {
        "vehicles": ["read"],
        "maintenance": ["read", "create", "update", "approve"],
        "inventory": ["read", "update"],
        "dashboard": ["read"],
        "reports": ["read"]
    },
    "Financial Operations": {
        "expenses": ["read", "create", "update", "approve", "export"],
        "reports": ["read", "export"],
        "fuel": ["read"],
        "dashboard": ["read"]
    },
    "Safety Operations": {
        "drivers": ["read", "update"],
        "vehicles": ["read"],
        "trips": ["read"],
        "reports": ["read"],
        "dashboard": ["read"]
    },
    "Procurement Operations": {
        "inventory": ["read", "create", "update", "approve"],
        "expenses": ["read", "create"],
        "reports": ["read"],
        "dashboard": ["read"]
    }
}
