"""
Routing & ETA Pydantic Schemas.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CoordinateLocation(BaseModel):
    """Geographic coordinate location."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    name: Optional[str] = None


class RouteLeg(BaseModel):
    """Single leg between two consecutive waypoints."""
    leg_index: int
    origin_name: str
    destination_name: str
    distance_km: float
    duration_minutes: float


class RouteCalculationRequest(BaseModel):
    """Request payload for route & ETA calculation."""
    origin: CoordinateLocation
    destination: CoordinateLocation
    waypoints: Optional[List[CoordinateLocation]] = None
    departure_time: Optional[datetime] = None
    average_speed_kmh: Optional[float] = Field(default=60.0, ge=10.0, le=150.0)


class RouteCalculationResponse(BaseModel):
    """Response payload with computed route metrics and geometry."""
    total_distance_km: float
    total_duration_minutes: float
    provider_used: str
    legs: List[RouteLeg]
    polyline_geometry: Optional[str] = None  # Encoded polyline or GEOJSON geometry


class StopETA(BaseModel):
    """Calculated ETA detail for a single trip stop."""
    model_config = ConfigDict(from_attributes=True)

    stop_id: UUID
    sequence: int
    location_name: str
    stop_type: str
    planned_arrival: datetime
    planned_departure: datetime
    distance_from_prev_km: float
    travel_time_from_prev_min: float
    dwell_time_minutes: int


class MultiStopETAResponse(BaseModel):
    """Response for multi-stop trip route & ETA calculation."""
    trip_id: UUID
    total_distance_km: float
    total_duration_minutes: float
    provider_used: str
    stops: List[StopETA]
    route_geometry: Optional[str] = None
