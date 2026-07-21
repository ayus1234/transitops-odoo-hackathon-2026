"""
Vehicle model for fleet management.
"""
from datetime import datetime, date
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, Date, DateTime, CheckConstraint, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Vehicle(Base):
    """
    Vehicle model representing fleet vehicles.
    
    Statuses:
    - Available: Ready for assignment
    - On Trip: Currently assigned to a trip
    - In Shop: Under maintenance
    - Retired: No longer in service
    """
    __tablename__ = "vehicles"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Registration and Identification
    registration_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )
    
    vehicle_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    vehicle_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    # Vehicle Details
    manufacturer: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    year: Mapped[Optional[int]] = mapped_column(
        nullable=True
    )
    
    # Capacity and Specifications
    capacity_kg: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    fuel_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    current_odometer_km: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0.0
    )
    
    # Financial Information
    acquisition_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )
    
    acquisition_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )
    
    # Insurance
    insurance_expiry: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Available',
        index=True
    )
    
    # Location Tracking
    latitude: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 6),
        nullable=True
    )
    
    longitude: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 6),
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
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('Available', 'On Trip', 'In Shop', 'Retired')",
            name="check_vehicle_status"
        ),
        CheckConstraint(
            "capacity_kg > 0",
            name="check_capacity_positive"
        ),
        CheckConstraint(
            "current_odometer_km >= 0",
            name="check_odometer_non_negative"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, registration={self.registration_number}, status={self.status})>"
    
    @property
    def is_available(self) -> bool:
        """Check if vehicle is available for assignment."""
        return self.status == 'Available'
    
    @property
    def is_operational(self) -> bool:
        """Check if vehicle is operational (not retired)."""
        return self.status != 'Retired'
