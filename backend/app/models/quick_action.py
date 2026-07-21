"""
Quick Actions models.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class QuickAction(Base):
    """Catalog of available quick actions."""
    __tablename__ = "quick_actions"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    route: Mapped[str] = mapped_column(String(255), nullable=False)
    http_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="GET")
    
    permission_resource: Mapped[str] = mapped_column(String(100), nullable=False)
    permission_action: Mapped[str] = mapped_column(String(50), nullable=False)
    
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=func.now(), nullable=False)


class UserFavoriteAction(Base):
    """User specific favorite actions."""
    __tablename__ = "user_favorite_actions"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_id: Mapped[UUID] = mapped_column(ForeignKey("quick_actions.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "action_id", name="uq_user_favorite_action"),
    )
    
    action = relationship("QuickAction")


class UserRecentAction(Base):
    """User specific recently executed actions."""
    __tablename__ = "user_recent_actions"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    action_id: Mapped[UUID] = mapped_column(ForeignKey("quick_actions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=func.now(), nullable=False)
    access_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    __table_args__ = (
        UniqueConstraint("user_id", "action_id", name="uq_user_recent_action"),
    )
    
    action = relationship("QuickAction")
