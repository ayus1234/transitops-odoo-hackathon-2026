"""
Audit Event Pydantic Schemas.
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AuditEventCreate(BaseModel):
    """Schema for recording a new audit event."""
    event_type: str = Field(..., max_length=50)
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID
    job_id: Optional[UUID] = None
    trip_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    payload: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None


class AuditEventResponse(BaseModel):
    """Schema for returning recorded audit events."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    entity_type: str
    entity_id: UUID
    job_id: Optional[UUID] = None
    trip_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    payload: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    created_at: datetime


class EventTimelineResponse(BaseModel):
    """Schema for a correlated entity event timeline."""
    entity_id: UUID
    entity_type: str
    total_events: int
    events: List[AuditEventResponse]
