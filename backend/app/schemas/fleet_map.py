from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class VehicleMarker(BaseModel):
    vehicle_id: UUID
    vehicle_name: str
    registration_number: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    driver_name: Optional[str] = None
    active_trip: Optional[str] = None
    has_critical_alert: bool = False
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DriverMarker(BaseModel):
    driver_id: UUID
    driver_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    assigned_vehicle: Optional[str] = None
    active_trip: Optional[str] = None
    has_critical_alert: bool = False
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TripMarker(BaseModel):
    trip_id: UUID
    origin: str
    destination: str
    trip_status: str
    estimated_arrival_time: Optional[datetime] = None
    vehicle_id: UUID
    driver_id: UUID
    route_information: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class FleetMapBounds(BaseModel):
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lng: Optional[float] = None
    max_lng: Optional[float] = None

class FullFleetMapResponse(BaseModel):
    vehicles: List[VehicleMarker]
    drivers: List[DriverMarker]
    trips: List[TripMarker]
    bounds: FleetMapBounds
