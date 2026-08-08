"""
Proof of Delivery (POD) Pydantic Schemas.
"""
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class PODSubmissionRequest(BaseModel):
    """Request payload for submitting Proof of Delivery on a trip stop."""
    receiver_name: str = Field(..., min_length=2, max_length=150, description="Full name of receiver")
    receiver_phone: Optional[str] = Field(default=None, max_length=30)
    signature_base64: Optional[str] = Field(default=None, description="Base64 encoded digital signature image")
    photo_url: Optional[str] = Field(default=None, description="URL or base64 of delivery photo proof")
    submitted_latitude: float = Field(..., ge=-90.0, le=90.0, description="GPS latitude at submission")
    submitted_longitude: float = Field(..., ge=-180.0, le=180.0, description="GPS longitude at submission")
    notes: Optional[str] = Field(default=None, max_length=500)


class PODResponse(BaseModel):
    """Response payload for Proof of Delivery verification."""
    model_config = ConfigDict(from_attributes=True)

    stop_id: UUID
    trip_id: UUID
    job_id: Optional[UUID] = None
    stop_sequence: int
    location_name: str
    stop_type: str
    stop_status: str
    delivered_at: datetime
    is_geofence_verified: bool
    geo_distance_offset_meters: float
    proof_of_delivery: Dict[str, Any]
    trip_completed: bool = False
