"""
Help Center models for knowledge base, support tickets, and feedback.
"""
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, CheckConstraint, func, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

JSONVariant = JSON().with_variant(JSONB, 'postgresql')
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HelpCategory(Base):
    """Category for grouping help articles."""
    __tablename__ = "help_categories"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=func.now(), nullable=False)
    
    # Relationships
    articles = relationship("HelpArticle", back_populates="category", cascade="all, delete-orphan")


class HelpArticle(Base):
    """Knowledge base article."""
    __tablename__ = "help_articles"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("help_categories.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    tags: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONVariant, nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("HelpCategory", back_populates="articles")
    author = relationship("User", foreign_keys=[created_by])


class SupportTicket(Base):
    """User submitted support ticket."""
    __tablename__ = "support_tickets"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    ticket_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default='Medium')
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='Open', index=True)
    
    assigned_to: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attachment_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=func.now(), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "priority IN ('Low', 'Medium', 'High', 'Critical')",
            name="check_ticket_priority"
        ),
        CheckConstraint(
            "status IN ('Open', 'In Progress', 'Resolved', 'Closed')",
            name="check_ticket_status"
        ),
    )
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])


class Feedback(Base):
    """User feedback for the platform."""
    __tablename__ = "feedback"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_feedback_rating"),
    )
    
    # Relationships
    user = relationship("User")
