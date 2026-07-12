"""
Trip model for fleet management.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, DateTime, Text, CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.driver import Driver
    from app.models.user import User


class Trip(Base):
    """
    Trip model representing trip records from dispatch to completion.
    
    Statuses:
    - Draft: Trip created but not yet dispatched
    - Dispatched: Trip is active, vehicle and driver are on trip
    - Completed: Trip finished successfully
    - Cancelled: Trip was cancelled
    
    Status Transitions:
    - Draft → Dispatched → Completed
    - Draft → Dispatched → Cancelled
    - Draft → Cancelled
    """
    __tablename__ = "trips"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Trip Identification
    trip_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Foreign Keys
    vehicle_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    driver_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Route Information
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Cargo
    cargo_weight_kg: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    # Distance
    planned_distance_km: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )
    
    actual_distance_km: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    # Timing
    planned_departure: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    actual_departure: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    planned_arrival: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Odometer
    start_odometer_km: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    end_odometer_km: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    # Fuel
    fuel_consumed_liters: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Draft',
        index=True
    )
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Created By
    created_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        lazy="joined",
        foreign_keys=[vehicle_id]
    )
    
    driver: Mapped["Driver"] = relationship(
        "Driver",
        lazy="joined",
        foreign_keys=[driver_id]
    )
    
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="joined",
        foreign_keys=[created_by]
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('Draft', 'Dispatched', 'Completed', 'Cancelled')",
            name="check_trip_status"
        ),
        CheckConstraint(
            "cargo_weight_kg > 0",
            name="check_cargo_weight_positive"
        ),
        CheckConstraint(
            "planned_distance_km > 0",
            name="check_planned_distance_positive"
        ),
        CheckConstraint(
            "actual_distance_km >= 0 OR actual_distance_km IS NULL",
            name="check_actual_distance_non_negative"
        ),
        CheckConstraint(
            "end_odometer_km >= start_odometer_km OR end_odometer_km IS NULL",
            name="check_odometer_order"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Trip(id={self.id}, trip_number={self.trip_number}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if trip is currently active (dispatched)."""
        return self.status == 'Dispatched'
    
    @property
    def is_draft(self) -> bool:
        """Check if trip is in draft state."""
        return self.status == 'Draft'
    
    @property
    def is_completed(self) -> bool:
        """Check if trip is completed."""
        return self.status == 'Completed'
    
    @property
    def is_cancelled(self) -> bool:
        """Check if trip is cancelled."""
        return self.status == 'Cancelled'
    
    @property
    def can_be_dispatched(self) -> bool:
        """Check if trip can be dispatched."""
        return self.status == 'Draft'
    
    @property
    def can_be_completed(self) -> bool:
        """Check if trip can be completed."""
        return self.status == 'Dispatched'
    
    @property
    def can_be_cancelled(self) -> bool:
        """Check if trip can be cancelled."""
        return self.status in ('Draft', 'Dispatched')
