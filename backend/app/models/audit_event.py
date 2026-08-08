"""
Audit Event SQLAlchemy Model.
Represents immutable lifecycle events for auditing, analytics, debugging, and notifications.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event Classification: JOB_CREATED, JOB_ASSIGNED, TRIP_CREATED, TRIP_STARTED, STOP_COMPLETED, DELIVERED, POD_RECEIVED, etc.
    event_type = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # Job, Trip, TripStop, Vehicle, Driver
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Correlated Domain Keys
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Detailed Event Context Payload
    payload = Column(JSONB, nullable=True)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index('ix_audit_events_job_timeline', 'job_id', 'created_at'),
        Index('ix_audit_events_trip_timeline', 'trip_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<AuditEvent(type={self.event_type}, entity={self.entity_type}, id={self.entity_id})>"
