"""
Application and Organization settings models.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, DateTime, Text, func
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ApplicationSettings(Base):
    """
    Singleton table for application-wide settings.
    Only one row should exist (key='default').
    """
    __tablename__ = "application_settings"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    key: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        default="default"
    )
    
    # Application Configuration
    app_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="TransitOps ERP"
    )
    
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UTC"
    )
    
    date_format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="YYYY-MM-DD"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR"
    )
    
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en"
    )
    
    maintenance_alert_days: Mapped[int] = mapped_column(
        nullable=False,
        default=7
    )
    
    license_expiry_alert_days: Mapped[int] = mapped_column(
        nullable=False,
        default=30
    )
    
    max_trip_duration_hours: Mapped[int] = mapped_column(
        nullable=False,
        default=24
    )
    
    auto_approve_expenses_below: Mapped[float] = mapped_column(
        nullable=False,
        default=0.0
    )
    
    # Feature Flags
    features: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<ApplicationSettings(key={self.key})>"


class OrganizationSettings(Base):
    """
    Singleton table for organization-level configuration.
    Only one row should exist (key='default').
    """
    __tablename__ = "organization_settings"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    key: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        default="default"
    )
    
    # Organization Information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="TransitOps Inc."
    )
    
    legal_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="admin@transitops.com"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    website: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    address_line2: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="India"
    )
    
    postal_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Tax & Registration
    tax_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    registration_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<OrganizationSettings(name={self.name})>"
