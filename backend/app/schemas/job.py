"""
Job Pydantic Schemas.
"""
from pydantic import BaseModel, ConfigDict, Field, UUID4
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class JobBase(BaseModel):
    customer_name: str = Field(..., max_length=255)
    customer_contact: Optional[str] = Field(None, max_length=255)
    pickup_address: str
    delivery_address: str
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    cargo_description: Optional[str] = None
    cargo_weight_kg: Optional[Decimal] = Field(None, ge=Decimal('0'))
    cargo_volume_cbm: Optional[Decimal] = Field(None, ge=Decimal('0'))
    priority: str = Field(default="Normal", description="Low, Normal, High, Urgent")
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    special_instructions: Optional[str] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_contact: Optional[str] = Field(None, max_length=255)
    pickup_address: Optional[str] = None
    delivery_address: Optional[str] = None
    pickup_latitude: Optional[float] = None
    pickup_longitude: Optional[float] = None
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    cargo_description: Optional[str] = None
    cargo_weight_kg: Optional[Decimal] = Field(None, ge=Decimal('0'))
    cargo_volume_cbm: Optional[Decimal] = Field(None, ge=Decimal('0'))
    priority: Optional[str] = None
    status: Optional[str] = None
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    special_instructions: Optional[str] = None
    trip_id: Optional[UUID4] = None


class JobResponse(JobBase):
    id: UUID4
    job_number: str
    status: str
    trip_id: Optional[UUID4] = None
    created_by_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    size: int
    pages: int
