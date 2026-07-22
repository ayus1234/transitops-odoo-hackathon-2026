"""
Expense schemas for request/response validation.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal


# ============================================================
# Shared summary schemas for nested responses
# ============================================================

class VehicleSummary(BaseModel):
    """Lightweight vehicle info for expense responses."""
    id: UUID
    registration_number: str
    model_config = ConfigDict(from_attributes=True)


class TripSummary(BaseModel):
    """Lightweight trip info for expense responses."""
    id: UUID
    trip_number: str
    model_config = ConfigDict(from_attributes=True)


class MaintenanceSummary(BaseModel):
    """Lightweight maintenance info for expense responses."""
    id: UUID
    maintenance_number: str
    model_config = ConfigDict(from_attributes=True)


class UserSummary(BaseModel):
    """Lightweight user info for expense responses."""
    id: UUID
    first_name: str
    last_name: str
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Enums/Constants
# ============================================================

VALID_EXPENSE_TYPES = ['Fuel', 'Maintenance', 'Toll', 'Repair', 'Miscellaneous']
VALID_EXPENSE_STATUSES = ['Pending', 'Approved', 'Rejected']


# ============================================================
# Request schemas
# ============================================================

class ExpenseCreate(BaseModel):
    """Schema for creating a new expense record."""

    expense_type: str = Field(..., description="Type of expense")
    amount: Decimal = Field(..., gt=0, description="Expense amount")
    expense_date: date = Field(..., description="Date of the expense")
    description: str = Field(..., min_length=1, description="Expense description")
    
    vehicle_id: Optional[UUID] = Field(None, description="Related vehicle ID")
    trip_id: Optional[UUID] = Field(None, description="Related trip ID")
    maintenance_id: Optional[UUID] = Field(None, description="Related maintenance ID")
    
    receipt_number: Optional[str] = Field(None, max_length=100)
    vendor_name: Optional[str] = Field(None, max_length=255)

    @field_validator('expense_type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_EXPENSE_TYPES:
            raise ValueError(f"Expense type must be one of: {', '.join(VALID_EXPENSE_TYPES)}")
        return v


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense record."""

    expense_type: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    expense_date: Optional[date] = None
    description: Optional[str] = Field(None, min_length=1)
    
    vehicle_id: Optional[UUID] = None
    trip_id: Optional[UUID] = None
    maintenance_id: Optional[UUID] = None
    
    receipt_number: Optional[str] = Field(None, max_length=100)
    vendor_name: Optional[str] = Field(None, max_length=255)

    @field_validator('expense_type')
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_EXPENSE_TYPES:
            raise ValueError(f"Expense type must be one of: {', '.join(VALID_EXPENSE_TYPES)}")
        return v


class ExpenseStatusUpdate(BaseModel):
    """Schema for approving or rejecting an expense."""
    reason: Optional[str] = Field(None, description="Reason for rejection (required if rejecting)")


# ============================================================
# Response schemas
# ============================================================

class ExpenseResponse(BaseModel):
    """Schema for full expense response."""

    id: UUID
    expense_type: str
    amount: Decimal
    expense_date: date
    description: str
    receipt_number: Optional[str]
    vendor_name: Optional[str]
    status: str
    
    vehicle: Optional[VehicleSummary]
    trip: Optional[TripSummary]
    maintenance: Optional[MaintenanceSummary]
    
    approver: Optional[UserSummary]
    recorder: Optional[UserSummary]
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    """Schema for expense list item."""

    id: UUID
    expense_type: str
    amount: Decimal
    expense_date: date
    description: str
    status: str
    vendor_name: Optional[str]
    
    vehicle: Optional[VehicleSummary]
    trip: Optional[TripSummary]

    model_config = ConfigDict(from_attributes=True)
