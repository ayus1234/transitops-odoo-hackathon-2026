"""
Vehicle schemas for request/response validation.
Extended with Vehicle 360 profile fields and expanded lifecycle states.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal

from app.models.vehicle import (
    VEHICLE_STATUSES, BODY_TYPES, POWERTRAIN_TYPES, OWNERSHIP_TYPES
)


class VehicleBase(BaseModel):
    """Base vehicle schema with common fields."""

    registration_number: str = Field(..., max_length=50, description="Vehicle registration number")
    vehicle_name: str = Field(..., max_length=100, description="Vehicle name/model")
    vehicle_type: str = Field(..., max_length=50, description="Vehicle type (Truck, Van, etc.)")
    manufacturer: Optional[str] = Field(None, max_length=100, description="Manufacturer name")
    model: Optional[str] = Field(None, max_length=100, description="Model name")
    year: Optional[int] = Field(None, ge=1900, le=2100, description="Manufacturing year")
    capacity_kg: Decimal = Field(..., gt=0, description="Maximum load capacity in kg")
    fuel_type: str = Field(..., max_length=50, description="Fuel type (Diesel, Petrol, CNG, Electric)")
    current_odometer_km: Decimal = Field(default=Decimal("0.0"), ge=0, description="Current odometer reading")
    acquisition_cost: Optional[Decimal] = Field(None, ge=0, description="Purchase cost")
    acquisition_date: Optional[date] = Field(None, description="Purchase date")
    insurance_expiry: Optional[date] = Field(None, description="Insurance expiry date")

    # Vehicle 360 fields
    vin: Optional[str] = Field(None, max_length=50, description="VIN / chassis number")
    variant: Optional[str] = Field(None, max_length=100, description="Vehicle variant/trim")
    body_type: Optional[str] = Field(None, max_length=50, description="Body type")
    powertrain: Optional[str] = Field(None, max_length=50, description="Powertrain type")
    seating_capacity: Optional[int] = Field(None, ge=1, description="Passenger seating capacity")
    ownership_type: Optional[str] = Field(None, max_length=20, description="Ownership type")
    lease_provider: Optional[str] = Field(None, max_length=255, description="Lease/rental provider")
    lease_start_date: Optional[date] = Field(None, description="Lease start date")
    lease_end_date: Optional[date] = Field(None, description="Lease end date")
    monthly_lease_cost: Optional[Decimal] = Field(None, ge=0, description="Monthly lease cost")
    engine_hours: Optional[Decimal] = Field(None, ge=0, description="Engine hours")
    notes: Optional[str] = Field(None, description="Notes")

    @field_validator('vehicle_type')
    @classmethod
    def validate_vehicle_type(cls, v: str) -> str:
        """Validate vehicle type."""
        allowed_types = ['Truck', 'Van', 'Pickup', 'Trailer', 'Bus', 'Car', 'Other']
        if v not in allowed_types:
            raise ValueError(f"Vehicle type must be one of: {', '.join(allowed_types)}")
        return v

    @field_validator('fuel_type')
    @classmethod
    def validate_fuel_type(cls, v: str) -> str:
        """Validate fuel type."""
        allowed_types = ['Diesel', 'Petrol', 'CNG', 'Electric', 'Hybrid']
        if v not in allowed_types:
            raise ValueError(f"Fuel type must be one of: {', '.join(allowed_types)}")
        return v

    @field_validator('body_type')
    @classmethod
    def validate_body_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate body type if provided."""
        if v is not None and v not in BODY_TYPES:
            raise ValueError(f"Body type must be one of: {', '.join(BODY_TYPES)}")
        return v

    @field_validator('powertrain')
    @classmethod
    def validate_powertrain(cls, v: Optional[str]) -> Optional[str]:
        """Validate powertrain type if provided."""
        if v is not None and v not in POWERTRAIN_TYPES:
            raise ValueError(f"Powertrain must be one of: {', '.join(POWERTRAIN_TYPES)}")
        return v

    @field_validator('ownership_type')
    @classmethod
    def validate_ownership_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate ownership type if provided."""
        if v is not None and v not in OWNERSHIP_TYPES:
            raise ValueError(f"Ownership type must be one of: {', '.join(OWNERSHIP_TYPES)}")
        return v


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle (all fields optional)."""

    registration_number: Optional[str] = Field(None, max_length=50)
    vehicle_name: Optional[str] = Field(None, max_length=100)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    capacity_kg: Optional[Decimal] = Field(None, gt=0)
    fuel_type: Optional[str] = Field(None, max_length=50)
    current_odometer_km: Optional[Decimal] = Field(None, ge=0)
    acquisition_cost: Optional[Decimal] = Field(None, ge=0)
    acquisition_date: Optional[date] = None
    insurance_expiry: Optional[date] = None
    status: Optional[str] = Field(None, max_length=20)

    # Vehicle 360 fields
    vin: Optional[str] = Field(None, max_length=50)
    variant: Optional[str] = Field(None, max_length=100)
    body_type: Optional[str] = Field(None, max_length=50)
    powertrain: Optional[str] = Field(None, max_length=50)
    seating_capacity: Optional[int] = Field(None, ge=1)
    ownership_type: Optional[str] = Field(None, max_length=20)
    lease_provider: Optional[str] = Field(None, max_length=255)
    lease_start_date: Optional[date] = None
    lease_end_date: Optional[date] = None
    monthly_lease_cost: Optional[Decimal] = Field(None, ge=0)
    engine_hours: Optional[Decimal] = Field(None, ge=0)
    retired_date: Optional[date] = None
    sale_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate vehicle status against expanded lifecycle states."""
        if v is not None:
            if v not in VEHICLE_STATUSES:
                raise ValueError(f"Status must be one of: {', '.join(VEHICLE_STATUSES)}")
        return v

    @field_validator('body_type')
    @classmethod
    def validate_body_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in BODY_TYPES:
            raise ValueError(f"Body type must be one of: {', '.join(BODY_TYPES)}")
        return v

    @field_validator('powertrain')
    @classmethod
    def validate_powertrain(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in POWERTRAIN_TYPES:
            raise ValueError(f"Powertrain must be one of: {', '.join(POWERTRAIN_TYPES)}")
        return v

    @field_validator('ownership_type')
    @classmethod
    def validate_ownership_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in OWNERSHIP_TYPES:
            raise ValueError(f"Ownership type must be one of: {', '.join(OWNERSHIP_TYPES)}")
        return v


class VehicleStatusUpdate(BaseModel):
    """Schema for explicit vehicle lifecycle status transition."""
    new_status: str = Field(..., description="Target lifecycle status")
    reason: Optional[str] = Field(None, description="Reason for status change")
    retired_date: Optional[date] = Field(None, description="Date of retirement (when retiring)")
    sale_price: Optional[Decimal] = Field(None, ge=0, description="Sale price (when selling)")

    @field_validator('new_status')
    @classmethod
    def validate_new_status(cls, v: str) -> str:
        if v not in VEHICLE_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VEHICLE_STATUSES)}")
        return v


class VehicleResponse(VehicleBase):
    """Schema for vehicle responses — includes all Vehicle 360 fields."""

    id: UUID
    status: str
    retired_date: Optional[date] = None
    sale_price: Optional[Decimal] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleListResponse(BaseModel):
    """Schema for vehicle list item (lighter than full response)."""

    id: UUID
    registration_number: str
    vehicle_name: str
    vehicle_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    capacity_kg: Decimal
    current_odometer_km: Decimal
    status: str
    fuel_type: str
    acquisition_cost: Optional[Decimal] = None
    ownership_type: Optional[str] = None
    body_type: Optional[str] = None
    powertrain: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Vehicle360Response(BaseModel):
    """Full Vehicle 360 profile response with aggregated data."""

    vehicle: VehicleResponse
    allowed_transitions: list[str] = []

    model_config = ConfigDict(from_attributes=True)
