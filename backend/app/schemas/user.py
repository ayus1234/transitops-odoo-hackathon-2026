"""
User schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.schemas.role import RoleResponse


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    """
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    role_id: UUID = Field(..., description="Role ID")


class UserUpdate(BaseModel):
    """
    Schema for updating a user.
    """
    email: EmailStr | None = None
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone_number: str | None = Field(None, max_length=20)
    role_id: UUID | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """
    Schema for user responses.
    """
    id: UUID
    full_name: str
    role: RoleResponse
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing user password.
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
