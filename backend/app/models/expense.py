"""
Expense model for operational expenses.
"""
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Numeric, DateTime, Date, Text, CheckConstraint, ForeignKey, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.trip import Trip
    from app.models.maintenance import Maintenance
    from app.models.user import User


class Expense(Base):
    """
    Expense model representing operational expenses.
    """
    __tablename__ = "expenses"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Core details
    expense_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    receipt_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    vendor_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default='Pending'
    )

    # Foreign Keys
    vehicle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    trip_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    maintenance_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("maintenance_logs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    approved_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    recorded_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
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
    vehicle: Mapped[Optional["Vehicle"]] = relationship(
        "Vehicle",
        lazy="joined",
        foreign_keys=[vehicle_id]
    )

    trip: Mapped[Optional["Trip"]] = relationship(
        "Trip",
        lazy="joined",
        foreign_keys=[trip_id]
    )

    maintenance: Mapped[Optional["Maintenance"]] = relationship(
        "Maintenance",
        lazy="joined",
        foreign_keys=[maintenance_id]
    )

    approver: Mapped[Optional["User"]] = relationship(
        "User",
        lazy="joined",
        foreign_keys=[approved_by]
    )

    recorder: Mapped["User"] = relationship(
        "User",
        lazy="joined",
        foreign_keys=[recorded_by]
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "expense_type IN ('Fuel', 'Maintenance', 'Toll', 'Repair', 'Miscellaneous')",
            name="check_expense_type"
        ),
        CheckConstraint(
            "status IN ('Pending', 'Approved', 'Rejected')",
            name="check_expense_status"
        ),
        CheckConstraint(
            "amount > 0",
            name="check_expense_amount_positive"
        ),
    )

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, type={self.expense_type}, amount={self.amount})>"
