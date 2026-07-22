"""
Fuel model for vehicle fuel consumption records.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, DateTime, Text, CheckConstraint, ForeignKey, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.trip import Trip
    from app.models.user import User


class Fuel(Base):
    """
    Fuel model representing vehicle fuel consumption records.
    """
    __tablename__ = "fuel_logs"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Foreign Keys
    vehicle_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    trip_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Fuel Details
    fuel_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    quantity_liters: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    cost_per_liter: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    total_cost: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    odometer_reading: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    refuel_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    station_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    receipt_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    # Created By
    recorded_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
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
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        lazy="joined",
        foreign_keys=[vehicle_id]
    )

    trip: Mapped[Optional["Trip"]] = relationship(
        "Trip",
        lazy="joined",
        foreign_keys=[trip_id]
    )

    recorder: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="joined",
        foreign_keys=[recorded_by]
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "quantity_liters > 0",
            name="check_fuel_quantity_positive"
        ),
        CheckConstraint(
            "cost_per_liter > 0",
            name="check_fuel_cost_per_liter_positive"
        ),
        CheckConstraint(
            "total_cost > 0",
            name="check_fuel_total_cost_positive"
        ),
        CheckConstraint(
            "odometer_reading >= 0",
            name="check_fuel_odometer_non_negative"
        ),
    )

    def __repr__(self) -> str:
        return f"<Fuel(id={self.id}, vehicle_id={self.vehicle_id}, qty={self.quantity_liters})>"
