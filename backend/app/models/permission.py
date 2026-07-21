"""
Permission model for granular access control.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, func, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Permission(Base):
    """
    Permission model defining granular access permissions.
    
    Permissions follow the resource:action pattern.
    Example: vehicles:read, trips:create, expenses:approve
    """
    __tablename__ = "permissions"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Permission Identity
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )
    
    resource: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name})>"
