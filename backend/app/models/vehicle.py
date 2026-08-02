"""
Vehicle model for fleet management.
Extended with Vehicle 360 profile columns and expanded lifecycle states.
"""
from datetime import datetime, date
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, Integer, Date, DateTime, Text, CheckConstraint, func, Index
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# Valid lifecycle states and allowed transitions
VEHICLE_STATUSES = [
    'Ordered', 'Acquired', 'Available', 'Assigned', 'Active',
    'On Trip', 'Maintenance', 'In Shop', 'Inactive', 'Retired', 'Sold'
]

VEHICLE_STATUS_TRANSITIONS = {
    'Ordered':     ['Acquired', 'Available'],
    'Acquired':    ['Available'],
    'Available':   ['Assigned', 'Active', 'On Trip', 'Maintenance', 'In Shop', 'Inactive', 'Retired'],
    'Assigned':    ['Active', 'On Trip', 'Available', 'Maintenance', 'In Shop'],
    'Active':      ['On Trip', 'Available', 'Maintenance', 'In Shop', 'Inactive'],
    'On Trip':     ['Available', 'Active', 'Assigned'],
    'Maintenance': ['Available', 'Active', 'Retired'],
    'In Shop':     ['Available', 'Active', 'Retired'],
    'Inactive':    ['Available', 'Active', 'Retired', 'Sold'],
    'Retired':     ['Sold'],
    'Sold':        [],
}

BODY_TYPES = [
    'Sedan', 'Hatchback', 'SUV', 'Truck', 'Van', 'Pickup',
    'Bus', 'Mini Bus', 'Trailer', 'Tanker', 'Flatbed', 'Refrigerated', 'Other'
]

POWERTRAIN_TYPES = ['ICE', 'Electric', 'Hybrid', 'CNG', 'LPG', 'Hydrogen', 'Other']

OWNERSHIP_TYPES = ['Owned', 'Leased', 'Rented', 'Loaned']


class Vehicle(Base):
    """
    Vehicle model representing fleet vehicles with comprehensive 360 profile.

    Lifecycle States:
    - Ordered: Purchased but not yet received
    - Acquired: Received but not yet prepared for operations
    - Available: Ready for assignment
    - Assigned: Assigned to a driver/route but not currently on trip
    - Active: In active operational use
    - On Trip: Currently on a trip
    - Maintenance / In Shop: Under maintenance or repair
    - Inactive: Temporarily out of service
    - Retired: Permanently decommissioned
    - Sold: Disposed/sold
    """
    __tablename__ = "vehicles"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # ── Registration and Identification ──
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

    # ── Vehicle 360 — Identification & Specs ──
    vin: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    manufacturer: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    model: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    variant: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    year: Mapped[Optional[int]] = mapped_column(
        nullable=True
    )

    body_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    powertrain: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    # ── Capacity and Specifications ──
    capacity_kg: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    seating_capacity: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
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

    engine_hours: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        default=0.0
    )

    # ── Financial / Acquisition ──
    acquisition_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    acquisition_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    # ── Ownership & Leasing ──
    ownership_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    lease_provider: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    lease_start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    lease_end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    monthly_lease_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    # ── Insurance (basic — detailed via Document model) ──
    insurance_expiry: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    # ── Status ──
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Available',
        index=True
    )

    # ── Location Tracking ──
    latitude: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 6),
        nullable=True
    )

    longitude: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 6),
        nullable=True
    )

    # ── Retirement / Disposal ──
    retired_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    sale_price: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    # ── Notes ──
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # ── Timestamps ──
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

    # ── Constraints ──
    __table_args__ = (
        CheckConstraint(
            "status IN ('Ordered', 'Acquired', 'Available', 'Assigned', 'Active', "
            "'On Trip', 'Maintenance', 'In Shop', 'Inactive', 'Retired', 'Sold')",
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
        Index('ix_vehicles_vin', 'vin', unique=True,
              postgresql_where=vin.isnot(None)),
    )

    def __repr__(self) -> str:
        return f"<Vehicle(id={self.id}, registration={self.registration_number}, status={self.status})>"

    # ── Properties ──
    @property
    def is_available(self) -> bool:
        """Check if vehicle is available for assignment."""
        return self.status == 'Available'

    @property
    def is_operational(self) -> bool:
        """Check if vehicle is operational (not retired/sold/inactive)."""
        return self.status not in ('Retired', 'Sold', 'Inactive')

    @property
    def is_in_fleet(self) -> bool:
        """Check if vehicle is part of the active fleet (not sold)."""
        return self.status != 'Sold'

    # ── Lifecycle Transition Validation ──
    def can_transition_to(self, new_status: str) -> bool:
        """Check if vehicle can transition to the given status."""
        if new_status not in VEHICLE_STATUSES:
            return False
        allowed = VEHICLE_STATUS_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def get_allowed_transitions(self) -> list[str]:
        """Get list of statuses this vehicle can transition to."""
        return list(VEHICLE_STATUS_TRANSITIONS.get(self.status, []))
