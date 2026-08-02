"""
Vendor schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal

from app.models.vendor import VENDOR_CATEGORIES


class VendorBase(BaseModel):
    """Base vendor schema with common fields."""

    vendor_code: str = Field(..., max_length=50, description="Unique vendor code")
    name: str = Field(..., max_length=255, description="Vendor / company name")
    contact_person: Optional[str] = Field(None, max_length=255, description="Contact person name")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    address: Optional[str] = Field(None, description="Physical address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=100, description="State / Province")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    categories: Optional[List[str]] = Field(default=[], description="Vendor categories (Parts, Service, Fuel, etc.)")
    payment_terms: Optional[str] = Field(None, max_length=100, description="Commercial payment terms")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax identification / GST / VAT number")
    is_active: bool = Field(default=True, description="Whether vendor is active")
    rating: Optional[Decimal] = Field(default=Decimal("5.00"), ge=Decimal("0"), le=Decimal("5"), description="Rating score out of 5.0")
    notes: Optional[str] = Field(None, description="Internal notes")

    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            for cat in v:
                if cat not in VENDOR_CATEGORIES:
                    raise ValueError(f"Category '{cat}' invalid. Allowed: {', '.join(VENDOR_CATEGORIES)}")
        return v


class VendorCreate(VendorBase):
    """Schema for creating a new vendor."""
    pass


class VendorUpdate(BaseModel):
    """Schema for updating a vendor (all fields optional)."""

    vendor_code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    categories: Optional[List[str]] = None
    payment_terms: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    rating: Optional[Decimal] = Field(None, ge=Decimal("0"), le=Decimal("5"))
    notes: Optional[str] = None

    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            for cat in v:
                if cat not in VENDOR_CATEGORIES:
                    raise ValueError(f"Category '{cat}' invalid. Allowed: {', '.join(VENDOR_CATEGORIES)}")
        return v


class VendorResponse(VendorBase):
    """Full vendor response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VendorListResponse(BaseModel):
    """Lightweight vendor response for list views and selectors."""

    id: UUID
    vendor_code: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    categories: Optional[List[str]] = []
    is_active: bool
    rating: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class VendorScorecardResponse(BaseModel):
    """Vendor performance scorecard schema."""

    vendor: VendorResponse
    purchase_orders_count: int = 0
    total_spend: Decimal = Decimal("0.00")
    active_contracts_count: int = 0

    model_config = ConfigDict(from_attributes=True)
