"""
Event-Driven Audit Trail API Router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import UUID4
from typing import Optional, List

from app.core.database import get_db
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User
from app.schemas.audit_event import AuditEventResponse, EventTimelineResponse
from app.services.audit_event_service import AuditEventService

router = APIRouter(prefix="/audit", tags=["Event-Driven Audit Trail"])


@router.get("/timeline/jobs/{job_id}", response_model=EventTimelineResponse)
def get_job_event_timeline(
    job_id: UUID4,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get full chronological lifecycle event history for a customer job."""
    service = AuditEventService(db)
    return service.get_job_timeline(job_id=job_id)


@router.get("/timeline/trips/{trip_id}", response_model=EventTimelineResponse)
def get_trip_event_timeline(
    trip_id: UUID4,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get full chronological lifecycle event history for an operational trip."""
    service = AuditEventService(db)
    return service.get_trip_timeline(trip_id=trip_id)


@router.get("/events", response_model=List[AuditEventResponse])
def list_recent_audit_events(
    event_type: Optional[str] = Query(default=None),
    entity_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Query recent operational audit log entries across the platform."""
    service = AuditEventService(db)
    return service.list_recent_events(event_type=event_type, entity_type=entity_type, limit=limit)
