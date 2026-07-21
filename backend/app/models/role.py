"""
Role model for RBAC (Role-Based Access Control).
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, DateTime, func, Boolean, ForeignKey, Table, Column
from sqlalchemy import Uuid as UUID, JSON as JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

user_additional_roles = Table(
    "user_additional_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)



class Role(Base):
    """
    Role model for defining user roles and permissions.
    
    Roles: Fleet Manager, Driver, Safety Officer, Financial Analyst
    """
    __tablename__ = "roles"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Basic Information
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )
    
    permissions: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    is_custom: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False
    )
    
    parent_role_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
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
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    
    parent: Mapped[Optional["Role"]] = relationship(
        "Role",
        remote_side="Role.id",
        back_populates="children"
    )
    
    children: Mapped[list["Role"]] = relationship(
        "Role",
        back_populates="parent"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
