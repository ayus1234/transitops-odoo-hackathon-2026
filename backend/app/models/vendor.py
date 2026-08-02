"""
Vendor model for vendor management and service provider directory.
"""
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4
from sqlalchemy import String, Numeric, Boolean, DateTime, Text, JSON, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


VENDOR_CATEGORIES = ['Parts', 'Service', 'Fuel', 'Tyres', 'Insurance', 'Logistics', 'Other']


class Vendor(Base):
    """
    Vendor model representing suppliers, service providers, and maintenance workshops.
    """
    __tablename__ = "vendors"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Identification
    vendor_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    # Contact Info
    contact_person: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    address: Mapped[Optional[str]] = mapped_column(
        Text,
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
        nullable=True
    )

    # Categorization & Commercials
    categories: Mapped[Optional[Any]] = mapped_column(
        JSON,
        nullable=True,
        default=list
    )

    payment_terms: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    tax_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    rating: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        default=5.00
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Vendor(id={self.id}, code={self.vendor_code}, name={self.name})>"
