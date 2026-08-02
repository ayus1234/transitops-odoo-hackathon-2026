"""
OdometerReading model for tracking vehicle odometer history.
Replaces reliance on a single mutable current_odometer_km field.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, DateTime, Text, ForeignKey, Index, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.trip import Trip
    from app.models.user import User


# Valid odometer reading sources
ODOMETER_SOURCES = ['manual', 'trip', 'maintenance', 'telemetry', 'import', 'correction']


class OdometerReading(Base):
    """
    Odometer reading model recording historical odometer snapshots.

    Every time an odometer value is observed (trip completion, maintenance,
    manual entry, telemetry ping, import), a reading is inserted here.
    The Vehicle.current_odometer_km is then updated to match.

    Anti-regression rule:
    New readings must be ≥ previous reading for the same vehicle,
    UNLESS the source is 'correction' (authorised override).
    """
    __tablename__ = "odometer_readings"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Vehicle FK
    vehicle_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Reading value
    reading_km: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    # When the reading was taken
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    # Source of the reading
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='manual'
    )

    # Who recorded it
    recorded_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Optional trip link (if reading came from trip completion)
    trip_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        lazy="joined",
        foreign_keys=[vehicle_id]
    )

    recorder: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="joined",
        foreign_keys=[recorded_by]
    )

    trip: Mapped[Optional["Trip"]] = relationship(
        "Trip",
        lazy="select",
        foreign_keys=[trip_id]
    )

    # Indexes for efficient queries
    __table_args__ = (
        Index('ix_odometer_vehicle_recorded', 'vehicle_id', 'recorded_at'),
    )

    def __repr__(self) -> str:
        return f"<OdometerReading(id={self.id}, vehicle={self.vehicle_id}, km={self.reading_km}, source={self.source})>"
