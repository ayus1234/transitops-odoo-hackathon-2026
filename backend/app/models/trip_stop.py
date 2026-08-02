"""
TripStop SQLAlchemy Model.
Represents waypoints and customer delivery/pickup stops on a multi-stop trip.
"""
from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class TripStop(Base):
    __tablename__ = "trip_stops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False, default=1)
    
    location_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Numeric(10, 6), nullable=True)
    longitude = Column(Numeric(10, 6), nullable=True)
    
    # Origin, Pickup, Waypoint, Delivery, Destination
    stop_type = Column(String(30), nullable=False, default="Waypoint")
    
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    
    planned_arrival = Column(DateTime(timezone=True), nullable=True)
    planned_departure = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    
    # Pending, Arrived, Completed, Skipped
    status = Column(String(20), nullable=False, default="Pending")
    
    proof_of_delivery = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    trip = relationship("Trip", foreign_keys=[trip_id], backref="stops")
    job = relationship("Job", back_populates="stops")
