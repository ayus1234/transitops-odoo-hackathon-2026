"""
Audit Event Recording & Timeline Analytics Service.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.schemas.audit_event import AuditEventCreate, AuditEventResponse, EventTimelineResponse
from app.utils.exceptions import NotFoundError


class AuditEventService:
    """Service for recording and querying immutable operational audit events."""

    def __init__(self, db: Session):
        self.db = db

    def record_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: UUID,
        summary: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        job_id: Optional[UUID] = None,
        trip_id: Optional[UUID] = None,
        vehicle_id: Optional[UUID] = None,
        driver_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None
    ) -> AuditEvent:
        """
        Record a new operational audit event in the database.
        """
        event = AuditEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            job_id=job_id,
            trip_id=trip_id,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            actor_id=actor_id,
            payload=payload or {},
            summary=summary or f"{event_type} recorded for {entity_type} {entity_id}"
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_job_timeline(self, job_id: UUID) -> EventTimelineResponse:
        """Get chronological event history for a customer Job."""
        events = self.db.query(AuditEvent).filter(
            AuditEvent.job_id == job_id
        ).order_by(AuditEvent.created_at.asc()).all()

        return EventTimelineResponse(
            entity_id=job_id,
            entity_type="Job",
            total_events=len(events),
            events=[AuditEventResponse.model_validate(e) for e in events]
        )

    def get_trip_timeline(self, trip_id: UUID) -> EventTimelineResponse:
        """Get chronological event history for a physical Trip."""
        events = self.db.query(AuditEvent).filter(
            AuditEvent.trip_id == trip_id
        ).order_by(AuditEvent.created_at.asc()).all()

        return EventTimelineResponse(
            entity_id=trip_id,
            entity_type="Trip",
            total_events=len(events),
            events=[AuditEventResponse.model_validate(e) for e in events]
        )

    def list_recent_events(
        self,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        limit: int = 50
    ) -> List[AuditEventResponse]:
        """Query recent audit log entries across the platform."""
        query = self.db.query(AuditEvent)
        if event_type:
            query = query.filter(AuditEvent.event_type == event_type)
        if entity_type:
            query = query.filter(AuditEvent.entity_type == entity_type)

        events = query.order_by(AuditEvent.created_at.desc()).limit(limit).all()
        return [AuditEventResponse.model_validate(e) for e in events]
