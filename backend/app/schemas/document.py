"""
Document schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator

from app.models.document import DOCUMENT_TYPES, DOCUMENT_STATUSES, VERIFICATION_STATES


class DocumentBase(BaseModel):
    """Base document schema with common fields."""
    document_type: str = Field(..., max_length=50, description="Type of document")
    document_number: Optional[str] = Field(None, max_length=100, description="Document/policy/certificate number")
    title: str = Field(..., max_length=255, description="Document title")
    issue_date: Optional[date] = Field(None, description="Issue date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    issuer: Optional[str] = Field(None, max_length=255, description="Issuing authority/company")
    notes: Optional[str] = Field(None, description="Additional notes")

    # Polymorphic links
    vehicle_id: Optional[UUID] = Field(None, description="Associated vehicle ID")
    driver_id: Optional[UUID] = Field(None, description="Associated driver ID")
    maintenance_id: Optional[UUID] = Field(None, description="Associated maintenance record ID")
    vendor_id: Optional[UUID] = Field(None, description="Associated vendor ID")

    @field_validator('document_type')
    @classmethod
    def validate_document_type(cls, v: str) -> str:
        if v not in DOCUMENT_TYPES:
            raise ValueError(f"Document type must be one of: {', '.join(DOCUMENT_TYPES)}")
        return v


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    file_path: Optional[str] = Field(None, max_length=500, description="Storage path or URI")
    file_name: Optional[str] = Field(None, max_length=255, description="File name")
    file_size_bytes: Optional[int] = Field(None, ge=0, description="File size in bytes")
    mime_type: Optional[str] = Field(None, max_length=100, description="MIME type")


class DocumentUpdate(BaseModel):
    """Schema for updating a document (all fields optional)."""
    document_type: Optional[str] = Field(None, max_length=50)
    document_number: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=255)
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuer: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None

    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    maintenance_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None

    @field_validator('document_type')
    @classmethod
    def validate_document_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DOCUMENT_TYPES:
            raise ValueError(f"Document type must be one of: {', '.join(DOCUMENT_TYPES)}")
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in DOCUMENT_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(DOCUMENT_STATUSES)}")
        return v


class DocumentVerifyRequest(BaseModel):
    """Schema for verifying/rejecting a document."""
    verification_state: str = Field(..., description="Target verification state (Verified or Rejected)")
    notes: Optional[str] = Field(None, description="Reason or verification notes")

    @field_validator('verification_state')
    @classmethod
    def validate_state(cls, v: str) -> str:
        allowed = ['Verified', 'Rejected']
        if v not in allowed:
            raise ValueError(f"Verification state must be one of: {', '.join(allowed)}")
        return v


class DocumentResponse(DocumentBase):
    """Full document response schema."""
    id: UUID
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    status: str
    verification_state: str
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    # Computed fields
    is_expired: bool = False
    days_until_expiry: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Lightweight document response for list views."""
    id: UUID
    document_type: str
    document_number: Optional[str] = None
    title: str
    expiry_date: Optional[date] = None
    status: str
    verification_state: str
    file_name: Optional[str] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None

    is_expired: bool = False
    days_until_expiry: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
