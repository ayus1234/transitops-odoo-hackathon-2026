from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer, func, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

JSONVariant = JSON().with_variant(JSONB, 'postgresql')

class CustomReport(Base):
    __tablename__ = "custom_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    module = Column(String, nullable=False)  # e.g., 'vehicles', 'trips'
    selected_fields = Column(JSONVariant, nullable=False)  # List of selected columns
    filters = Column(JSONVariant, nullable=True)  # List of filter conditions
    group_by = Column(String, nullable=True)
    sort_by = Column(String, nullable=True)
    sort_order = Column(String, nullable=True)  # 'asc' or 'desc'
    chart_type = Column(String, nullable=True)
    export_formats = Column(JSONVariant, nullable=True)  # e.g., ["csv", "pdf"]
    is_public = Column(Boolean, default=False)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User")
    executions = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")
    schedules = relationship("ScheduledReport", back_populates="report", cascade="all, delete-orphan")


class ReportExecution(Base):
    __tablename__ = "report_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("custom_reports.id", ondelete="CASCADE"), nullable=False)
    executed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    execution_time = Column(DateTime(timezone=True), server_default=func.now())
    duration_ms = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False)  # 'success', 'failed'
    row_count = Column(Integer, nullable=False, default=0)
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("CustomReport", back_populates="executions")
    executor = relationship("User")


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("custom_reports.id", ondelete="CASCADE"), nullable=False)
    frequency = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly', 'custom'
    cron_expression = Column(String, nullable=True)
    next_run = Column(DateTime(timezone=True), nullable=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    email_recipients = Column(JSONVariant, nullable=True)  # List of emails
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    report = relationship("CustomReport", back_populates="schedules")
