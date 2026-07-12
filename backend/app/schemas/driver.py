"""
Driver schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal

from app.schemas.user import UserResponse


class DriverBase(BaseModel):
    """Base driver schema with common fields."""
    
    license_number: str = Field(..., max_length=50, description="Driving license number")
    license_category: str = Field(..., max_length=50, description="License category (LMV, HMV, etc.)")
    license_issue_date: date = Field(..., description="License issue date")
    license_expiry_date: date = Field(..., description="License expiry date")
    date_of_birth: date = Field(..., description="Driver date of birth")
    emergency_contact: Optional[str] = Field(None, max_length=20, description="Emergency contact number")
    
    @field_validator('license_expiry_date')
    @classmethod
    def validate_license_expiry(cls, v: date, info) -> date:
        """Validate license expiry date."""
        if 'license_issue_date' in info.data and v <= info.data['license_issue_date']:
            raise ValueError("License expiry date must be after issue date")
        return v
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Validate driver is at least 18 years old."""
        from datetime import date as date_class
        today = date_class.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Driver must be at least 18 years old")
        return v


class DriverCreate(DriverBase):
    """Schema for creating a new driver with user information."""
    
    user: dict = Field(..., description="User account information")
    
    @field_validator('license_expiry_date')
    @classmethod
    def validate_not_expired(cls, v: date) -> date:
        """Ensure license is not already expired when creating driver."""
        from datetime import date as date_class
        if v < date_class.today():
            raise ValueError("Cannot create driver with expired license")
        return v


class DriverUpdate(BaseModel):
    """Schema for updating a driver."""
    
    license_number: Optional[str] = Field(None, max_length=50)
    license_category: Optional[str] = Field(None, max_length=50)
    license_issue_date: Optional[date] = None
    license_expiry_date: Optional[date] = None
    date_of_birth: Optional[date] = None
    emergency_contact: Optional[str] = Field(None, max_length=20)
    safety_score: Optional[Decimal] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, max_length=20)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate driver status."""
        if v is not None:
            allowed_statuses = ['Available', 'On Trip', 'Off Duty', 'Suspended']
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator('safety_score')
    @classmethod
    def validate_safety_score(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate safety score range."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Safety score must be between 0 and 100")
        return v


class DriverResponse(DriverBase):
    """Schema for driver responses."""
    
    id: UUID
    user_id: UUID
    user: UserResponse
    safety_score: Decimal
    total_trips: int
    status: str
    joined_date: date
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DriverListResponse(BaseModel):
    """Schema for driver list item (lighter than full response)."""
    
    id: UUID
    user_id: UUID
    user: UserResponse
    license_number: str
    license_category: str
    license_expiry_date: date
    safety_score: Decimal
    total_trips: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)


class DriverPerformance(BaseModel):
    """Schema for driver performance metrics."""
    
    driver_id: UUID
    driver_name: str
    total_trips: int
    safety_score: Decimal
    average_fuel_efficiency: Optional[Decimal] = None
    on_time_delivery_pct: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)
