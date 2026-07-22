"""
Settings schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


# ──────────────────────────────────────────────────────────────
# Application Settings
# ──────────────────────────────────────────────────────────────

VALID_TIMEZONES = [
    "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
    "Europe/London", "Europe/Berlin", "Europe/Paris",
    "Asia/Kolkata", "Asia/Tokyo", "Asia/Shanghai", "Asia/Dubai",
    "Australia/Sydney", "America/Sao_Paulo", "Africa/Nairobi",
]

VALID_CURRENCIES = [
    "USD", "EUR", "GBP", "INR", "JPY", "CNY", "AED", "AUD",
    "BRL", "CAD", "CHF", "KES", "NGN", "ZAR", "SGD",
]

VALID_LANGUAGES = ["en", "hi", "es", "fr", "de", "pt", "ar", "zh", "ja"]

VALID_DATE_FORMATS = [
    "YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD-MM-YYYY",
]


class ApplicationSettingsResponse(BaseModel):
    """Schema for application settings response."""
    id: UUID
    app_name: str
    timezone: str
    date_format: str
    currency: str
    language: str
    maintenance_alert_days: int
    license_expiry_alert_days: int
    max_trip_duration_hours: int
    auto_approve_expenses_below: float
    features: Dict[str, Any]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationSettingsUpdate(BaseModel):
    """Schema for updating application settings."""
    app_name: Optional[str] = Field(None, min_length=1, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    language: Optional[str] = Field(None, max_length=10)
    maintenance_alert_days: Optional[int] = Field(None, ge=1, le=90)
    license_expiry_alert_days: Optional[int] = Field(None, ge=1, le=365)
    max_trip_duration_hours: Optional[int] = Field(None, ge=1, le=168)
    auto_approve_expenses_below: Optional[float] = Field(None, ge=0)
    features: Optional[Dict[str, Any]] = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        if v is not None and v not in VALID_TIMEZONES:
            raise ValueError(f"Invalid timezone. Must be one of: {', '.join(VALID_TIMEZONES)}")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        if v is not None and v not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency ISO code. Must be one of: {', '.join(VALID_CURRENCIES)}")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if v is not None and v not in VALID_LANGUAGES:
            raise ValueError(f"Invalid language. Must be one of: {', '.join(VALID_LANGUAGES)}")
        return v

    @field_validator("date_format")
    @classmethod
    def validate_date_format(cls, v):
        if v is not None and v not in VALID_DATE_FORMATS:
            raise ValueError(f"Invalid date format. Must be one of: {', '.join(VALID_DATE_FORMATS)}")
        return v


# ──────────────────────────────────────────────────────────────
# Organization Settings
# ──────────────────────────────────────────────────────────────

class OrganizationSettingsResponse(BaseModel):
    """Schema for organization settings response."""
    id: UUID
    name: str
    legal_name: Optional[str]
    email: str
    phone: Optional[str]
    website: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    tax_id: Optional[str]
    registration_number: Optional[str]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationSettingsUpdate(BaseModel):
    """Schema for updating organization settings."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    legal_name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    tax_id: Optional[str] = Field(None, max_length=50)
    registration_number: Optional[str] = Field(None, max_length=50)


# ──────────────────────────────────────────────────────────────
# Permission Schemas
# ──────────────────────────────────────────────────────────────

class PermissionResponse(BaseModel):
    """Schema for permission response."""
    id: UUID
    name: str
    resource: str
    action: str
    description: Optional[str]
    is_system: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionAssign(BaseModel):
    """Schema for assigning a permission to a role."""
    role_id: UUID = Field(..., description="Target role ID")
    resource: str = Field(..., min_length=1, max_length=50, description="Resource name (e.g. vehicles)")
    action: str = Field(..., min_length=1, max_length=50, description="Action name (e.g. read)")


class PermissionRemove(BaseModel):
    """Schema for removing a permission from a role."""
    role_id: UUID = Field(..., description="Target role ID")
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)


# ──────────────────────────────────────────────────────────────
# Admin User Management Schemas
# ──────────────────────────────────────────────────────────────

class AdminUserUpdate(BaseModel):
    """Schema for admin updating a user."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    role_id: Optional[UUID] = None


class AdminUserResponse(BaseModel):
    """Schema for admin user listing response."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone_number: Optional[str]
    is_active: bool
    role_id: UUID
    role_name: str
    additional_roles: Optional[List[Dict[str, Any]]] = None
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminResetPassword(BaseModel):
    """Schema for admin resetting a user's password."""
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")


# ──────────────────────────────────────────────────────────────
# Role Management (Extended)
# ──────────────────────────────────────────────────────────────

class AdminRoleCreate(BaseModel):
    """Schema for creating a new role via admin panel."""
    name: str = Field(..., min_length=1, max_length=50, description="Unique role name")
    permissions: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Permissions map: {resource: [actions]}"
    )


class AdminRoleUpdate(BaseModel):
    """Schema for updating a role via admin panel."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    permissions: Optional[Dict[str, List[str]]] = None
