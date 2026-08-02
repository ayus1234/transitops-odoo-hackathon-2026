"""
Job SQLAlchemy Model.
Repated to logistics / customer shipping orders.
"""
from sqlalchemy import Column, String, Text, Numeric, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class JobPriorityEnum(str, enum.Enum):
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


class JobStatusEnum(str, enum.Enum):
    DRAFT = "Draft"
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    customer_contact = Column(String(255), nullable=True)
    
    pickup_address = Column(Text, nullable=False)
    delivery_address = Column(Text, nullable=False)
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    
    cargo_description = Column(Text, nullable=True)
    cargo_weight_kg = Column(Numeric(10, 2), nullable=True)
    cargo_volume_cbm = Column(Numeric(10, 2), nullable=True)
    
    priority = Column(String(20), nullable=False, default="Normal", index=True)
    time_window_start = Column(DateTime(timezone=True), nullable=True)
    time_window_end = Column(DateTime(timezone=True), nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    status = Column(String(20), nullable=False, default="Pending", index=True)
    
    # FKs
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    trip = relationship("Trip", foreign_keys=[trip_id], backref="jobs")
    created_by = relationship("User", foreign_keys=[created_by_id])
    stops = relationship("TripStop", back_populates="job")
