"""
Odometer reading schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal

from app.models.odometer_reading import ODOMETER_SOURCES


class OdometerReadingCreate(BaseModel):
    """Schema for recording a new odometer reading."""
    reading_km: Decimal = Field(..., ge=0, description="Odometer reading in kilometers")
    recorded_at: Optional[datetime] = Field(None, description="When the reading was taken (defaults to now)")
    source: str = Field(default="manual", description="Source of the reading")
    trip_id: Optional[UUID] = Field(None, description="Associated trip ID")
    notes: Optional[str] = Field(None, description="Notes about the reading")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v: str) -> str:
        if v not in ODOMETER_SOURCES:
            raise ValueError(f"Source must be one of: {', '.join(ODOMETER_SOURCES)}")
        return v


class OdometerReadingResponse(BaseModel):
    """Schema for odometer reading response."""
    id: UUID
    vehicle_id: UUID
    reading_km: Decimal
    recorded_at: datetime
    source: str
    recorded_by: Optional[UUID] = None
    trip_id: Optional[UUID] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OdometerStatsResponse(BaseModel):
    """Schema for odometer distance/utilisation statistics."""
    vehicle_id: UUID
    current_odometer_km: Decimal
    total_readings: int
    first_reading_km: Optional[Decimal] = None
    last_reading_km: Optional[Decimal] = None
    first_reading_date: Optional[datetime] = None
    last_reading_date: Optional[datetime] = None
    total_distance_km: Optional[Decimal] = None
