"""
Fuel schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal


# ============================================================
# Shared summary schemas for nested responses
# ============================================================

class VehicleSummary(BaseModel):
    """Lightweight vehicle info for fuel responses."""

    id: UUID
    registration_number: str
    vehicle_name: str
    fuel_type: str

    model_config = ConfigDict(from_attributes=True)


class TripSummary(BaseModel):
    """Lightweight trip info for fuel responses."""

    id: UUID
    trip_number: str

    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    """Lightweight user info for fuel responses."""

    id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Request schemas
# ============================================================

VALID_FUEL_TYPES = ['Diesel', 'Petrol', 'CNG', 'Electric']


class FuelCreate(BaseModel):
    """Schema for creating a new fuel record."""

    vehicle_id: UUID = Field(..., description="Vehicle being refueled")
    trip_id: Optional[UUID] = Field(None, description="Associated trip")
    fuel_type: str = Field(..., max_length=50, description="Type of fuel")
    quantity_liters: Decimal = Field(..., gt=0, description="Quantity in liters")
    cost_per_liter: Decimal = Field(..., gt=0, description="Cost per liter")
    odometer_reading: Decimal = Field(..., ge=0, description="Odometer reading at refueling")
    refuel_date: Optional[datetime] = Field(None, description="Refuel date (defaults to now)")
    station_name: Optional[str] = Field(None, max_length=255, description="Fuel station name")
    location: Optional[str] = Field(None, max_length=255, description="Refueling location")
    receipt_number: Optional[str] = Field(None, max_length=100, description="Receipt number")

    @field_validator('fuel_type')
    @classmethod
    def validate_fuel_type(cls, v: str) -> str:
        if v not in VALID_FUEL_TYPES:
            raise ValueError(f"Fuel type must be one of: {', '.join(VALID_FUEL_TYPES)}")
        return v


class FuelUpdate(BaseModel):
    """Schema for updating a fuel record."""

    vehicle_id: Optional[UUID] = None
    trip_id: Optional[UUID] = None
    fuel_type: Optional[str] = Field(None, max_length=50)
    quantity_liters: Optional[Decimal] = Field(None, gt=0)
    cost_per_liter: Optional[Decimal] = Field(None, gt=0)
    odometer_reading: Optional[Decimal] = Field(None, ge=0)
    refuel_date: Optional[datetime] = None
    station_name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    receipt_number: Optional[str] = Field(None, max_length=100)

    @field_validator('fuel_type')
    @classmethod
    def validate_fuel_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_FUEL_TYPES:
            raise ValueError(f"Fuel type must be one of: {', '.join(VALID_FUEL_TYPES)}")
        return v


# ============================================================
# Response schemas
# ============================================================

class FuelResponse(BaseModel):
    """Schema for full fuel response."""

    id: UUID
    vehicle: VehicleSummary
    trip: Optional[TripSummary]
    fuel_type: str
    quantity_liters: Decimal
    cost_per_liter: Decimal
    total_cost: Decimal
    odometer_reading: Decimal
    refuel_date: datetime
    station_name: Optional[str]
    location: Optional[str]
    receipt_number: Optional[str]
    recorder: Optional[UserSummary]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FuelListResponse(BaseModel):
    """Schema for fuel list item (lighter than full response)."""

    id: UUID
    vehicle: VehicleSummary
    trip: Optional[TripSummary]
    fuel_type: str
    quantity_liters: Decimal
    cost_per_liter: Decimal
    total_cost: Decimal
    odometer_reading: Decimal
    refuel_date: datetime
    station_name: Optional[str]
    location: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class FuelEfficiencyStats(BaseModel):
    """Schema for fuel efficiency statistics."""
    
    vehicle_id: UUID
    registration_number: str
    avg_fuel_efficiency_kmpl: Decimal
    total_fuel_consumed: Decimal
    total_distance: Decimal

    model_config = ConfigDict(from_attributes=True)
