"""
Maintenance schemas for request/response validation.
"""
from datetime import datetime, date, time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal


# ============================================================
# Shared summary schemas for nested responses
# ============================================================

class VehicleSummary(BaseModel):
    """Lightweight vehicle info for maintenance responses."""

    id: UUID
    registration_number: str
    vehicle_name: str

    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    """Lightweight user info for maintenance responses."""

    id: UUID
    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Request schemas
# ============================================================

VALID_MAINTENANCE_TYPES = [
    'Oil Change', 'Tire Replacement', 'Engine Repair',
    'Brake Service', 'Battery Replacement', 'Transmission Service',
    'AC Service', 'General Inspection', 'Body Repair', 'Other'
]

VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

VALID_STATUSES = ['Pending', 'Approved', 'In Progress', 'Completed', 'Rejected']


class MaintenanceCreate(BaseModel):
    """Schema for creating a new maintenance record."""

    vehicle_id: UUID = Field(..., description="Vehicle to maintain")
    maintenance_type: str = Field(..., max_length=100, description="Type of maintenance")
    description: str = Field(..., min_length=1, description="Detailed description")
    priority: str = Field(default="Medium", max_length=20, description="Priority level")
    assigned_technician: Optional[str] = Field(None, max_length=100, description="Technician name")
    scheduled_date: date = Field(..., description="Scheduled maintenance date")
    estimated_cost: Optional[Decimal] = Field(None, ge=0, description="Estimated cost")
    odometer_at_maintenance: Optional[Decimal] = Field(None, ge=0, description="Odometer reading")
    start_time: Optional[time] = Field(None, description="Scheduled start time")
    end_time: Optional[time] = Field(None, description="Scheduled end time")
    estimated_duration: Optional[int] = Field(None, ge=0, description="Estimated duration in minutes")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('maintenance_type')
    @classmethod
    def validate_maintenance_type(cls, v: str) -> str:
        """Validate maintenance type."""
        if v not in VALID_MAINTENANCE_TYPES:
            raise ValueError(
                f"Maintenance type must be one of: {', '.join(VALID_MAINTENANCE_TYPES)}"
            )
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority."""
        if v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        return v


class MaintenanceUpdate(BaseModel):
    """Schema for updating a maintenance record (only Pending/Approved)."""

    maintenance_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, max_length=20)
    assigned_technician: Optional[str] = Field(None, max_length=100)
    scheduled_date: Optional[date] = None
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    odometer_at_maintenance: Optional[Decimal] = Field(None, ge=0)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    estimated_duration: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

    @field_validator('maintenance_type')
    @classmethod
    def validate_maintenance_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_MAINTENANCE_TYPES:
            raise ValueError(
                f"Maintenance type must be one of: {', '.join(VALID_MAINTENANCE_TYPES)}"
            )
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}")
        return v


class MaintenanceStatusUpdate(BaseModel):
    """Schema for updating maintenance status (PATCH status endpoint)."""

    status: str = Field(..., description="New maintenance status")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
        return v


class MaintenanceComplete(BaseModel):
    """Schema for completing maintenance."""

    completed_date: date = Field(..., description="Actual completion date")
    actual_cost: Decimal = Field(..., ge=0, description="Actual cost")
    notes: Optional[str] = Field(None, description="Completion notes")


class MaintenanceReschedule(BaseModel):
    """Schema for rescheduling maintenance."""

    scheduled_date: date = Field(..., description="New scheduled date")
    start_time: Optional[time] = Field(None, description="New start time")
    end_time: Optional[time] = Field(None, description="New end time")
    estimated_duration: Optional[int] = Field(None, ge=0, description="New duration in minutes")


# ============================================================
# Response schemas
# ============================================================

class MaintenanceResponse(BaseModel):
    """Schema for full maintenance response."""

    id: UUID
    maintenance_number: str
    vehicle: VehicleSummary
    maintenance_type: str
    description: str
    priority: str
    assigned_technician: Optional[str]
    scheduled_date: date
    completed_date: Optional[date]
    start_time: Optional[time]
    end_time: Optional[time]
    estimated_duration: Optional[int]
    estimated_cost: Optional[Decimal]
    actual_cost: Optional[Decimal]
    odometer_at_maintenance: Optional[Decimal]
    status: str
    notes: Optional[str]
    creator: Optional[UserSummary]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaintenanceListResponse(BaseModel):
    """Schema for maintenance list item (lighter than full response)."""

    id: UUID
    maintenance_number: str
    vehicle: VehicleSummary
    maintenance_type: str
    description: str
    priority: str
    assigned_technician: Optional[str]
    scheduled_date: date
    start_time: Optional[time]
    end_time: Optional[time]
    estimated_duration: Optional[int]
    status: str
    estimated_cost: Optional[Decimal]

    model_config = ConfigDict(from_attributes=True)


class CalendarEventResponse(BaseModel):
    """Schema for maintenance calendar event."""

    id: UUID
    title: str
    description: str
    vehicle_id: UUID
    vehicle_name: str
    technician_name: Optional[str]
    maintenance_type: str
    priority: str
    status: str
    scheduled_date: date
    start_time: Optional[time]
    end_time: Optional[time]
    estimated_duration: Optional[int]
    color: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
