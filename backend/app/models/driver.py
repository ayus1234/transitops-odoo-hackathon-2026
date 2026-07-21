"""
Driver model for fleet management.
"""
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, Date, DateTime, Integer, CheckConstraint, ForeignKey, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Driver(Base):
    """
    Driver model representing fleet drivers with license information.
    
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
    
    license_issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    
    license_expiry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    
    # Personal Information
    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )
    
    emergency_contact: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Performance Metrics
    safety_score: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=100.00
    )
    
    total_trips: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
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
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="driver",
        lazy="joined",
        foreign_keys=[user_id]
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
        from datetime import date as date_class
        return self.license_expiry_date > date_class.today()
    
    @property
    def can_be_assigned(self) -> bool:
        """Check if driver can be assigned to a trip."""
        return self.is_available and self.is_license_valid
