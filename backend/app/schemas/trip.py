"""
Trip schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from decimal import Decimal


class VehicleSummary(BaseModel):
    """Lightweight vehicle info for trip responses."""
    
    id: UUID
    registration_number: str
    vehicle_name: str
    
    model_config = ConfigDict(from_attributes=True)


class DriverSummary(BaseModel):
    """Lightweight driver info for trip responses."""
    
    id: UUID
    license_number: str
    
    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    """Lightweight user info for trip responses."""
    
    id: UUID
    first_name: str
    last_name: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)


class TripCreate(BaseModel):
    """Schema for creating a new trip."""
    
    vehicle_id: UUID = Field(..., description="Assigned vehicle ID")
    driver_id: UUID = Field(..., description="Assigned driver ID")
    source: str = Field(..., max_length=255, description="Origin location")
    destination: str = Field(..., max_length=255, description="Destination location")
    cargo_weight_kg: Decimal = Field(..., gt=0, description="Cargo weight in kg")
    planned_distance_km: Decimal = Field(..., gt=0, description="Planned distance in km")
    planned_departure: datetime = Field(..., description="Planned departure time")
    planned_arrival: datetime = Field(..., description="Planned arrival time")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @model_validator(mode='after')
    def validate_times(self):
        """Validate planned arrival is after planned departure."""
        if self.planned_arrival <= self.planned_departure:
            raise ValueError("Planned arrival must be after planned departure")
        return self


class TripUpdate(BaseModel):
    """Schema for updating a trip (only while in Draft status)."""
    
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    source: Optional[str] = Field(None, max_length=255)
    destination: Optional[str] = Field(None, max_length=255)
    cargo_weight_kg: Optional[Decimal] = Field(None, gt=0)
    planned_distance_km: Optional[Decimal] = Field(None, gt=0)
    planned_departure: Optional[datetime] = None
    planned_arrival: Optional[datetime] = None
    notes: Optional[str] = None


class TripDispatch(BaseModel):
    """Schema for dispatching a trip."""
    
    start_odometer_km: Decimal = Field(..., ge=0, description="Odometer reading at start")


class TripComplete(BaseModel):
    """Schema for completing a trip."""
    
    end_odometer_km: Decimal = Field(..., ge=0, description="Odometer reading at end")
    actual_distance_km: Decimal = Field(..., ge=0, description="Actual distance traveled")
    fuel_consumed_liters: Optional[Decimal] = Field(None, ge=0, description="Fuel consumed in liters")
    notes: Optional[str] = Field(None, description="Completion notes")


class TripCancel(BaseModel):
    """Schema for cancelling a trip."""
    
    reason: str = Field(..., min_length=1, max_length=500, description="Cancellation reason")


class TripResponse(BaseModel):
    """Schema for full trip response."""
    
    id: UUID
    trip_number: str
    vehicle: VehicleSummary
    driver: DriverSummary
    source: str
    destination: str
    cargo_weight_kg: Decimal
    planned_distance_km: Decimal
    actual_distance_km: Optional[Decimal]
    planned_departure: datetime
    actual_departure: Optional[datetime]
    planned_arrival: datetime
    actual_arrival: Optional[datetime]
    start_odometer_km: Optional[Decimal]
    end_odometer_km: Optional[Decimal]
    fuel_consumed_liters: Optional[Decimal]
    status: str
    notes: Optional[str]
    creator: Optional[UserSummary]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TripListResponse(BaseModel):
    """Schema for trip list item (lighter than full response)."""
    
    id: UUID
    trip_number: str
    vehicle: VehicleSummary
    driver: DriverSummary
    source: str
    destination: str
    cargo_weight_kg: Decimal
    planned_distance_km: Decimal
    planned_departure: datetime
    planned_arrival: datetime
    status: str
    
    model_config = ConfigDict(from_attributes=True)
