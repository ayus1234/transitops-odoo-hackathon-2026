"""
Vehicle Telemetry & IoT Pydantic Schemas.
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TelemetryRecord(BaseModel):
    """Single GPS & OBD-II telemetry reading from a vehicle or IoT device."""
    vehicle_id: Optional[UUID] = None
    registration_number: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: Optional[float] = Field(default=0.0)
    speed_kmh: float = Field(default=0.0, ge=0.0)
    heading: Optional[float] = Field(default=0.0, ge=0.0, le=360.0)
    accuracy_m: Optional[float] = Field(default=5.0)
    ignition: bool = Field(default=True)
    fuel_level_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    engine_temp_c: Optional[float] = Field(default=None)
    battery_voltage: Optional[float] = Field(default=None)
    odometer_km: Optional[float] = Field(default=None, ge=0.0)
    engine_rpm: Optional[float] = Field(default=None)
    diagnostics: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class TelemetryIngestBatchRequest(BaseModel):
    """Batch payload for high-throughput IoT gateway telemetry ingestion."""
    device_id: Optional[str] = None
    records: List[TelemetryRecord] = Field(..., min_length=1)


class TelemetryIngestResponse(BaseModel):
    """Response payload summarizing batch processing results."""
    records_processed: int
    alerts_triggered: int
    live_broadcasted: bool
    timestamps_range: Dict[str, str]


class TelemetryLogResponse(BaseModel):
    """Historical telemetry breadcrumb record."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vehicle_id: UUID
    trip_id: Optional[UUID] = None
    latitude: float
    longitude: float
    speed_kmh: float
    heading: float
    ignition: bool
    fuel_level_percent: Optional[float] = None
    odometer_km: Optional[float] = None
    timestamp: datetime


class FleetLiveLocationResponse(BaseModel):
    """Current live location and operational state of a vehicle."""
    vehicle_id: UUID
    registration_number: str
    vehicle_name: str
    vehicle_type: str
    status: str
    is_online: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    speed_kmh: float = 0.0
    heading: float = 0.0
    last_ping_at: Optional[datetime] = None
    active_trip_id: Optional[UUID] = None
    driver_name: Optional[str] = None
