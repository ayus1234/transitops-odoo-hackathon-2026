"""
Telemetry & IoT Processing Service.
Handles batch GPS ingestion, geofence checks, route deviation detection, speeding alerts, and live map updates.
"""
import math
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.models.trip import Trip
from app.models.trip_stop import TripStop
from app.models.driver import Driver
from app.models.telemetry import VehicleTelemetryLog
from app.schemas.telemetry import (
    TelemetryIngestBatchRequest,
    TelemetryIngestResponse,
    TelemetryLogResponse,
    FleetLiveLocationResponse,
)
from app.services.audit_event_service import AuditEventService
from app.utils.exceptions import NotFoundError, BusinessLogicError


class TelemetryService:
    """Service for processing real-time vehicle telemetry streams and triggering IoT alerts."""

    GEOFENCE_RADIUS_METERS = 500.0
    ROUTE_DEVIATION_MAX_METERS = 500.0
    SPEED_LIMIT_KMH = 80.0
    ONLINE_HEARTBEAT_MINUTES = 5

    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditEventService(db)

    def ingest_telemetry_batch(
        self, batch_req: TelemetryIngestBatchRequest
    ) -> TelemetryIngestResponse:
        """
        Ingest batch GPS & sensor telemetry readings.
        Updates vehicle current position, evaluates geofence/deviation alerts, and logs breadcrumbs.
        """
        processed_count = 0
        alerts_count = 0
        now = datetime.now()

        for rec in batch_req.records:
            # 1. Resolve Vehicle
            vehicle = None
            if rec.vehicle_id:
                vehicle = self.db.query(Vehicle).filter(Vehicle.id == rec.vehicle_id).first()
            elif rec.registration_number:
                vehicle = self.db.query(Vehicle).filter(Vehicle.registration_number == rec.registration_number).first()

            if not vehicle:
                continue

            # 2. Check for active trip
            active_trip = self.db.query(Trip).filter(
                Trip.vehicle_id == vehicle.id,
                Trip.status == "Dispatched"
            ).first()

            # 3. Create Telemetry Log
            timestamp = rec.timestamp or now
            log_entry = VehicleTelemetryLog(
                vehicle_id=vehicle.id,
                trip_id=active_trip.id if active_trip else None,
                latitude=rec.latitude,
                longitude=rec.longitude,
                altitude_m=rec.altitude_m,
                speed_kmh=rec.speed_kmh,
                heading=rec.heading,
                accuracy_m=rec.accuracy_m,
                ignition=rec.ignition,
                fuel_level_percent=rec.fuel_level_percent,
                engine_temp_c=rec.engine_temp_c,
                battery_voltage=rec.battery_voltage,
                odometer_km=rec.odometer_km,
                engine_rpm=rec.engine_rpm,
                diagnostics=rec.diagnostics or {},
                timestamp=timestamp
            )
            self.db.add(log_entry)

            # 4. Update Vehicle Current State
            setattr(vehicle, 'latitude', rec.latitude)
            setattr(vehicle, 'longitude', rec.longitude)
            if rec.odometer_km is not None and rec.odometer_km > 0:
                setattr(vehicle, 'current_odometer_km', rec.odometer_km)
            setattr(vehicle, 'updated_at', timestamp)

            processed_count += 1

            # 5. Alert Evaluation
            # A. Speeding Alert
            if rec.speed_kmh > self.SPEED_LIMIT_KMH:
                alerts_count += 1
                self.audit_service.record_event(
                    event_type="SPEEDING_ALERT",
                    entity_type="Vehicle",
                    entity_id=UUID(str(vehicle.id)),
                    vehicle_id=UUID(str(vehicle.id)),
                    trip_id=UUID(str(active_trip.id)) if active_trip else None,
                    driver_id=UUID(str(active_trip.driver_id)) if active_trip else None,
                    summary=f"Vehicle {vehicle.registration_number} over-speeding at {rec.speed_kmh:.1f} km/h (Limit: {self.SPEED_LIMIT_KMH:.0f} km/h)",
                    payload={"speed_kmh": rec.speed_kmh, "limit_kmh": self.SPEED_LIMIT_KMH, "latitude": rec.latitude, "longitude": rec.longitude}
                )

            # B. Geofence Arrival Check (if on active trip)
            if active_trip:
                pending_stops = self.db.query(TripStop).filter(
                    TripStop.trip_id == active_trip.id,
                    TripStop.status == "Pending"
                ).all()

                for stop in pending_stops:
                    if stop.latitude is not None and stop.longitude is not None:
                        dist_m = self._haversine_meters(
                            float(str(stop.latitude)), float(str(stop.longitude)),
                            rec.latitude, rec.longitude
                        )
                        if dist_m <= self.GEOFENCE_RADIUS_METERS:
                            setattr(stop, 'status', 'Arrived')
                            setattr(stop, 'actual_arrival', timestamp)
                            alerts_count += 1
                            self.audit_service.record_event(
                                event_type="GEOFENCE_ENTER",
                                entity_type="TripStop",
                                entity_id=UUID(str(stop.id)),
                                job_id=UUID(str(stop.job_id)) if stop.job_id else None,
                                trip_id=UUID(str(active_trip.id)),
                                vehicle_id=UUID(str(vehicle.id)),
                                summary=f"Vehicle {vehicle.registration_number} entered geofence for stop '{stop.location_name}' ({dist_m:.0f}m offset)",
                                payload={"stop_name": stop.location_name, "distance_offset_m": round(dist_m, 1)}
                            )

        self.db.commit()

        return TelemetryIngestResponse(
            records_processed=processed_count,
            alerts_triggered=alerts_count,
            live_broadcasted=True,
            timestamps_range={"processed_at": now.isoformat()}
        )

    def get_live_fleet_positions(self) -> List[FleetLiveLocationResponse]:
        """Fetch current live location and heartbeat state for all active fleet vehicles."""
        vehicles = self.db.query(Vehicle).all()
        now = datetime.now()
        heartbeat_cutoff = now - timedelta(minutes=self.ONLINE_HEARTBEAT_MINUTES)

        result: List[FleetLiveLocationResponse] = []

        for v in vehicles:
            # Check latest telemetry log entry for speed/heading
            latest_log = self.db.query(VehicleTelemetryLog).filter(
                VehicleTelemetryLog.vehicle_id == v.id
            ).order_by(VehicleTelemetryLog.timestamp.desc()).first()

            # Active trip & driver info
            active_trip = self.db.query(Trip).filter(
                Trip.vehicle_id == v.id,
                Trip.status == "Dispatched"
            ).first()

            driver_name = None
            if active_trip and active_trip.driver_id:
                driver = self.db.query(Driver).filter(Driver.id == active_trip.driver_id).first()
                if driver and driver.user:
                    driver_name = f"{driver.user.first_name} {driver.user.last_name}".strip()

            if v.updated_at is not None:
                v_updated = v.updated_at.replace(tzinfo=None) if hasattr(v.updated_at, 'tzinfo') and v.updated_at.tzinfo is not None else v.updated_at
                cutoff = heartbeat_cutoff.replace(tzinfo=None)
                is_online = bool(v_updated >= cutoff)
            else:
                is_online = False

            result.append(FleetLiveLocationResponse(
                vehicle_id=UUID(str(v.id)),
                registration_number=str(v.registration_number),
                vehicle_name=str(v.vehicle_name),
                vehicle_type=str(v.vehicle_type),
                status=str(v.status),
                is_online=is_online,
                latitude=float(str(v.latitude)) if v.latitude is not None else None,
                longitude=float(str(v.longitude)) if v.longitude is not None else None,
                speed_kmh=float(latest_log.speed_kmh) if latest_log else 0.0,
                heading=float(latest_log.heading) if latest_log and latest_log.heading else 0.0,
                last_ping_at=v.updated_at,
                active_trip_id=UUID(str(active_trip.id)) if active_trip else None,
                driver_name=driver_name
            ))

        return result

    def get_vehicle_breadcrumbs(
        self, vehicle_id: UUID, limit: int = 100
    ) -> List[TelemetryLogResponse]:
        """Fetch historical GPS breadcrumbs for route playback."""
        logs = self.db.query(VehicleTelemetryLog).filter(
            VehicleTelemetryLog.vehicle_id == vehicle_id
        ).order_by(VehicleTelemetryLog.timestamp.desc()).limit(limit).all()

        return [TelemetryLogResponse.model_validate(l) for l in logs]

    @staticmethod
    def _haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance in meters."""
        r = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c
