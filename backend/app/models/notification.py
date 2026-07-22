"""
Notification model for the Notification Center.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any
from uuid import uuid4
from sqlalchemy import String, Text, Boolean, DateTime, CheckConstraint, ForeignKey, func, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

JSONVariant = JSON().with_variant(JSONB(), 'postgresql')

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    """
    Notification model representing system notifications to users.
    """
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    module_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="System"
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Info"
    )

    icon_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    route: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    related_entity_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
        index=True
    )

    metadata_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONVariant,
        nullable=True,
        name="metadata" # Map metadata_payload to DB column "metadata" to avoid conflict with SQLAlchemy Base.metadata
    )

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
        lazy="select"
    )

    __table_args__ = (
        CheckConstraint(
            "priority IN ('Low', 'Medium', 'High', 'Critical')",
            name="check_notification_priority"
        ),
        CheckConstraint(
            "category IN ('Vehicles', 'Drivers', 'Trips', 'Maintenance', 'Fuel', 'Expenses', 'Reports', 'Settings', 'Quick Actions', 'System')",
            name="check_notification_category"
        ),
        CheckConstraint(
            "type IN ('Info', 'Success', 'Warning', 'Critical')",
            name="check_notification_type"
        ),
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"
