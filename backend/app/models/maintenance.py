"""
Maintenance model for vehicle maintenance records.
"""
from datetime import datetime, date, time
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, DateTime, Date, Time, Integer, Text, CheckConstraint, ForeignKey, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.user import User


class Maintenance(Base):
    """
    Maintenance model representing vehicle maintenance/service records.

    Statuses:
    - Pending: Maintenance scheduled but not yet approved
    - Approved: Maintenance approved, awaiting work
    - In Progress: Work is being done (vehicle is 'In Shop')
    - Completed: Maintenance finished successfully
    - Rejected: Maintenance request was rejected

    Status Transitions:
    - Pending → Approved → In Progress → Completed
    - Pending → Rejected
    - Approved → Rejected

    Business Rules:
    - Setting status to 'In Progress' sets vehicle.status = 'In Shop'
    - Setting status to 'Completed' restores vehicle.status = 'Available'
    """
    __tablename__ = "maintenance_logs"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Maintenance Identification
    maintenance_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    # Foreign Keys
    vehicle_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Maintenance Details
    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Medium'
    )

    assigned_technician: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    # Dates
    scheduled_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    completed_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    start_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    end_time: Mapped[Optional[time]] = mapped_column(
        Time,
        nullable=True
    )

    estimated_duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    # Costs
    estimated_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    actual_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    # Odometer
    odometer_at_maintenance: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Pending',
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

    creator: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="joined",
        foreign_keys=[created_by]
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('Pending', 'Approved', 'In Progress', 'Completed', 'Rejected')",
            name="check_maintenance_status"
        ),
        CheckConstraint(
            "priority IN ('Low', 'Medium', 'High', 'Critical')",
            name="check_maintenance_priority"
        ),
        CheckConstraint(
            "estimated_cost >= 0 OR estimated_cost IS NULL",
            name="check_estimated_cost_non_negative"
        ),
        CheckConstraint(
            "actual_cost >= 0 OR actual_cost IS NULL",
            name="check_actual_cost_non_negative"
        ),
    )

    def __repr__(self) -> str:
        return f"<Maintenance(id={self.id}, number={self.maintenance_number}, status={self.status})>"

    @property
    def is_pending(self) -> bool:
        """Check if maintenance is pending."""
        return self.status == 'Pending'

    @property
    def is_approved(self) -> bool:
        """Check if maintenance is approved."""
        return self.status == 'Approved'

    @property
    def is_in_progress(self) -> bool:
        """Check if maintenance is in progress."""
        return self.status == 'In Progress'

    @property
    def is_completed(self) -> bool:
        """Check if maintenance is completed."""
        return self.status == 'Completed'

    @property
    def is_rejected(self) -> bool:
        """Check if maintenance is rejected."""
        return self.status == 'Rejected'

    @property
    def can_be_approved(self) -> bool:
        """Check if maintenance can be approved."""
        return self.status == 'Pending'

    @property
    def can_start(self) -> bool:
        """Check if maintenance can start."""
        return self.status == 'Approved'

    @property
    def can_be_completed(self) -> bool:
        """Check if maintenance can be completed."""
        return self.status == 'In Progress'

    @property
    def can_be_rejected(self) -> bool:
        """Check if maintenance can be rejected."""
        return self.status in ('Pending', 'Approved')
