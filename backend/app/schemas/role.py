"""
Role schemas for request/response validation.
"""
from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class RoleBase(BaseModel):
    """
    Base role schema with common fields.
    """
    name: str = Field(..., max_length=50, description="Role name")
    permissions: Dict[str, Any] = Field(default_factory=dict, description="Role permissions")


class RoleCreate(RoleBase):
    """
    Schema for creating a new role.
    """
    pass


class RoleUpdate(BaseModel):
    """
    Schema for updating a role.
    """
    name: str | None = Field(None, max_length=50)
    permissions: Dict[str, Any] | None = None


class RoleResponse(RoleBase):
    """
    Schema for role responses.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
