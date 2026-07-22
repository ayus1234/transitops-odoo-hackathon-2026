"""
Permission Audit Log model for tracking RBAC changes.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PermissionAuditLog(Base):
    """
    Audit log for tracking all RBAC changes.
    """
    __tablename__ = "permission_audit_logs"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )
    
    # Who performed the action
    user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # What action was performed (e.g., 'UPDATE_ROLE', 'ASSIGN_ROLE')
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    # What module/resource was affected
    module: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Affected targets
    target_role_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True
    )
    
    target_user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Change payloads
    previous_value: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )
    
    new_value: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )
    
    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Relationships for quick access (lazy load)
    actor = relationship("User", foreign_keys=[user_id], lazy="select")
    target_user = relationship("User", foreign_keys=[target_user_id], lazy="select")
    target_role = relationship("Role", foreign_keys=[target_role_id], lazy="select")

    def __repr__(self) -> str:
        return f"<PermissionAuditLog(id={self.id}, action={self.action})>"
