"""
Driver model for fleet management.
Extended with Driver 360 profile fields and multi-factor performance metrics.
"""
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, Date, DateTime, Integer, Text, CheckConstraint, ForeignKey, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vehicle import Vehicle


class Driver(Base):
    """
    Driver model representing fleet drivers with license information and 360 profile.

    Statuses:
    - Available: Ready for trip assignment
    - On Trip: Currently on a trip
    - Off Duty: Not available for work
    - Suspended: Suspended from driving
    """
    __tablename__ = "drivers"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # User Relationship
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # License Information
    license_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    license_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    license_class: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    license_issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    license_expiry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    # Personal & Medical Information
    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    blood_group: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    medical_fitness_expiry: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    # Performance & Scoring Metrics
    safety_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=100.00
    )

    efficiency_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        default=100.00
    )

    compliance_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        default=100.00
    )

    overall_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        default=100.00
    )

    total_trips: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # Current Assignment
    current_vehicle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Status and Dates
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Available',
        index=True
    )

    joined_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=func.current_date()
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

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="driver",
        lazy="joined",
        foreign_keys=[user_id]
    )

    current_vehicle: Mapped[Optional["Vehicle"]] = relationship(
        "Vehicle",
        lazy="joined",
        foreign_keys=[current_vehicle_id]
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('Available', 'On Trip', 'Off Duty', 'Suspended')",
            name="check_driver_status"
        ),
        CheckConstraint(
            "safety_score >= 0 AND safety_score <= 100",
            name="check_safety_score_range"
        ),
        CheckConstraint(
            "total_trips >= 0",
            name="check_total_trips_non_negative"
        ),
        CheckConstraint(
            "license_expiry_date > license_issue_date",
            name="check_license_dates"
        ),
    )

    def __repr__(self) -> str:
        return f"<Driver(id={self.id}, license={self.license_number}, status={self.status})>"

    @property
    def is_available(self) -> bool:
        """Check if driver is available for assignment."""
        return self.status == 'Available'

    @property
    def is_license_valid(self) -> bool:
        """Check if driver's license is still valid."""
        return self.license_expiry_date > date.today()

    @property
    def is_medical_valid(self) -> bool:
        """Check if driver's medical fitness is valid."""
        if not self.medical_fitness_expiry:
            return True
        return self.medical_fitness_expiry > date.today()

    @property
    def can_be_assigned(self) -> bool:
        """Check if driver can be assigned to a trip."""
        return self.is_available and self.is_license_valid and self.is_medical_valid
