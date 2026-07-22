"""
Vehicle schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal


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


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle."""
    
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
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate vehicle status."""
        if v is not None:
            allowed_statuses = ['Available', 'On Trip', 'In Shop', 'Retired']
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class VehicleResponse(VehicleBase):
    """Schema for vehicle responses."""
    
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class VehicleListResponse(BaseModel):
    """Schema for vehicle list item (lighter than full response)."""
    
    id: UUID
    registration_number: str
    vehicle_name: str
    vehicle_type: str
    capacity_kg: Decimal
    current_odometer_km: Decimal
    status: str
    fuel_type: str
    acquisition_cost: Optional[Decimal]
    
    model_config = ConfigDict(from_attributes=True)
