"""
User model for authentication and authorization.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.driver import Driver


class User(Base):
    """
    User model representing system users with authentication.
    """
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Basic Information
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Role and Status
    role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Activity Tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
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
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
        lazy="joined"
    )
    
    additional_roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_additional_roles",
        lazy="select"
    )
    
    driver: Mapped[Optional["Driver"]] = relationship(
        "Driver",
        back_populates="user",
        uselist=False,
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.name if self.role else None})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    def get_all_permissions(self) -> dict:
        """Aggregate permissions from primary role, additional roles, and their parents."""
        if not self.role:
            return {}
            
        all_perms = {}
        
        def merge_perms(target: dict, source: dict):
            for res, actions in source.items():
                if res not in target:
                    target[res] = set(actions)
                else:
                    target[res].update(actions)
                    
        def extract_role_tree(role: "Role"):
            if role.permissions:
                merge_perms(all_perms, role.permissions)
            if hasattr(role, "parent") and role.parent:
                extract_role_tree(role.parent)
                
        # Primary role tree
        extract_role_tree(self.role)
        
        # Additional roles tree
        if self.additional_roles:
            for ar in self.additional_roles:
                extract_role_tree(ar)
                
        # Convert sets back to lists
        return {res: list(actions) for res, actions in all_perms.items()}

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has a specific permission."""
        if resource in ["dashboard", "reports", "settings", "help_center"]:
            return True
            
        if self.role and self.role.name in ["Super Admin", "Administrator", "System Admin"]:
            return True
            
        aggregated_perms = self.get_all_permissions()
        resource_permissions = aggregated_perms.get(resource, [])
        return action in resource_permissions
