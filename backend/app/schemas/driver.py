"""
Driver schemas for request/response validation.
Extended with Driver 360 profile fields and score breakdowns.
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal

from app.schemas.user import UserResponse
from app.schemas.vehicle import VehicleListResponse


class DriverBase(BaseModel):
    """Base driver schema with common fields."""

    license_number: str = Field(..., max_length=50, description="Driving license number")
    license_category: str = Field(..., max_length=50, description="License category (LMV, HMV, etc.)")
    license_issue_date: date = Field(..., description="License issue date")
    license_expiry_date: date = Field(..., description="License expiry date")
    date_of_birth: date = Field(..., description="Driver date of birth")
    emergency_contact: Optional[str] = Field(None, max_length=20, description="Emergency contact number")

    # Driver 360 fields
    license_class: Optional[str] = Field(None, max_length=50, description="Detailed license class (e.g. HGV, MCWG)")
    blood_group: Optional[str] = Field(None, max_length=10, description="Blood group (e.g. A+, O-)")
    medical_fitness_expiry: Optional[date] = Field(None, description="Medical fitness certificate expiry date")
    notes: Optional[str] = Field(None, description="Notes")

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
    status: Optional[str] = Field(None, max_length=20)

    # Driver 360 fields
    license_class: Optional[str] = Field(None, max_length=50)
    blood_group: Optional[str] = Field(None, max_length=10)
    medical_fitness_expiry: Optional[date] = None
    safety_score: Optional[Decimal] = Field(None, ge=Decimal('0'), le=Decimal('100'))
    efficiency_score: Optional[Decimal] = Field(None, ge=Decimal('0'), le=Decimal('100'))
    compliance_score: Optional[Decimal] = Field(None, ge=Decimal('0'), le=Decimal('100'))
    overall_score: Optional[Decimal] = Field(None, ge=Decimal('0'), le=Decimal('100'))
    current_vehicle_id: Optional[UUID] = None
    notes: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate driver status."""
        if v is not None:
            allowed_statuses = ['Available', 'On Trip', 'Off Duty', 'Suspended']
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v

    @field_validator('safety_score', 'efficiency_score', 'compliance_score', 'overall_score')
    @classmethod
    def validate_score_range(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate score range."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Score must be between 0 and 100")
        return v


class DriverResponse(DriverBase):
    """Schema for driver responses."""

    id: UUID
    user_id: UUID
    user: UserResponse
    safety_score: Decimal
    efficiency_score: Optional[Decimal] = Decimal("100.00")
    compliance_score: Optional[Decimal] = Decimal("100.00")
    overall_score: Optional[Decimal] = Decimal("100.00")
    total_trips: int
    status: str
    current_vehicle_id: Optional[UUID] = None
    current_vehicle: Optional[VehicleListResponse] = None
    joined_date: date
    created_at: datetime
    updated_at: datetime

    is_license_valid: bool = True
    is_medical_valid: bool = True

    model_config = ConfigDict(from_attributes=True)


class DriverListResponse(BaseModel):
    """Schema for driver list item (lighter than full response)."""

    id: UUID
    user_id: UUID
    user: UserResponse
    license_number: str
    license_category: str
    license_class: Optional[str] = None
    license_expiry_date: date
    safety_score: Decimal
    efficiency_score: Optional[Decimal] = Decimal("100.00")
    compliance_score: Optional[Decimal] = Decimal("100.00")
    overall_score: Optional[Decimal] = Decimal("100.00")
    total_trips: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class DriverPerformance(BaseModel):
    """Schema for driver performance metrics."""

    driver_id: UUID
    driver_name: str
    total_trips: int
    safety_score: Decimal
    efficiency_score: Optional[Decimal] = Decimal("100.00")
    compliance_score: Optional[Decimal] = Decimal("100.00")
    overall_score: Optional[Decimal] = Decimal("100.00")
    average_fuel_efficiency: Optional[Decimal] = None
    on_time_delivery_pct: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class Driver360Response(BaseModel):
    """Full Driver 360 profile response with aggregated metrics."""

    driver: DriverResponse
    documents_count: int = 0
    recent_trips_count: int = 0

    model_config = ConfigDict(from_attributes=True)
