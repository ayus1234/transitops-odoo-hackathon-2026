"""
Proof of Delivery (POD) Service.
Handles digital signature capture, photo attachments, geofence verification, and status auto-transitions.
"""
import math
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.trip_stop import TripStop
from app.models.trip import Trip
from app.models.job import Job
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.schemas.pod import PODSubmissionRequest, PODResponse
from app.utils.exceptions import NotFoundError, BusinessLogicError


class PODService:
    """Proof of Delivery verification and workflow service."""

    GEOFENCE_RADIUS_METERS = 500.0  # Max allowed distance offset for geofence validation

    def __init__(self, db: Session):
        self.db = db

    def submit_proof_of_delivery(
        self,
        stop_id: UUID,
        req: PODSubmissionRequest
    ) -> PODResponse:
        """
        Submit Proof of Delivery for a trip stop.
        Validates geofence proximity, updates JSONB proof, and triggers trip/job completion logic.
        """
        stop = self.db.query(TripStop).filter(TripStop.id == stop_id).first()
        if not stop:
            raise NotFoundError(f"Trip stop with ID '{stop_id}' not found.")

        if stop.status == "Completed":
            raise BusinessLogicError(f"Trip stop '{stop.location_name}' is already completed.")

        trip = self.db.query(Trip).filter(Trip.id == stop.trip_id).first()
        if not trip:
            raise NotFoundError(f"Associated trip '{stop.trip_id}' not found.")

        now = datetime.now()

        # 1. Geofence Verification
        stop_lat = float(str(stop.latitude)) if stop.latitude is not None else None
        stop_lng = float(str(stop.longitude)) if stop.longitude is not None else None

        if stop_lat is not None and stop_lng is not None:
            dist_meters = self._haversine_meters(
                stop_lat, stop_lng,
                req.submitted_latitude, req.submitted_longitude
            )
            is_geofence_valid = dist_meters <= self.GEOFENCE_RADIUS_METERS
        else:
            dist_meters = 0.0
            is_geofence_valid = True

        # 2. Build POD JSONB Payload
        pod_payload = {
            "receiver_name": req.receiver_name,
            "receiver_phone": req.receiver_phone,
            "signature_base64": req.signature_base64,
            "photo_url": req.photo_url,
            "submitted_latitude": req.submitted_latitude,
            "submitted_longitude": req.submitted_longitude,
            "geo_distance_offset_meters": round(dist_meters, 1),
            "is_geofence_verified": is_geofence_valid,
            "delivered_at": now.isoformat(),
            "notes": req.notes
        }

        # 3. Update TripStop Record
        setattr(stop, 'proof_of_delivery', pod_payload)
        setattr(stop, 'status', 'Completed')
        if getattr(stop, 'actual_arrival', None) is None:
            setattr(stop, 'actual_arrival', now)
        setattr(stop, 'actual_departure', now)

        # 4. Link Job State Update
        if stop.job_id:
            job = self.db.query(Job).filter(Job.id == stop.job_id).first()
            if job:
                setattr(job, 'status', 'Delivered')

        # 5. Check Overall Trip Completion
        all_stops = self.db.query(TripStop).filter(TripStop.trip_id == trip.id).all()
        incomplete_stops = [
            s for s in all_stops 
            if s.id != stop.id and s.status not in ["Completed", "Skipped"] and s.stop_type != "Origin"
        ]

        trip_completed = False
        if len(incomplete_stops) == 0:
            setattr(trip, 'status', 'Completed')
            setattr(trip, 'actual_arrival', now)
            trip_completed = True

            # Release vehicle & driver back to Available status
            vehicle = self.db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
            if vehicle and vehicle.status in ["In Transit", "On Trip", "Active", "Assigned"]:
                setattr(vehicle, 'status', 'Available')

            driver = self.db.query(Driver).filter(Driver.id == trip.driver_id).first()
            if driver and driver.status in ["In Transit", "On Trip", "Active", "Assigned"]:
                setattr(driver, 'status', 'Available')

        self.db.commit()
        self.db.refresh(stop)

        # Record Audit Events
        try:
            from app.services.audit_event_service import AuditEventService
            audit = AuditEventService(self.db)

            # Event 1: POD_RECEIVED
            audit.record_event(
                event_type="POD_RECEIVED",
                entity_type="TripStop",
                entity_id=UUID(str(stop.id)),
                job_id=UUID(str(stop.job_id)) if stop.job_id else None,
                trip_id=UUID(str(stop.trip_id)),
                vehicle_id=UUID(str(trip.vehicle_id)),
                driver_id=UUID(str(trip.driver_id)),
                summary=f"Proof of Delivery submitted for stop '{stop.location_name}' by receiver {req.receiver_name}",
                payload=pod_payload
            )

            # Event 2: STOP_COMPLETED
            audit.record_event(
                event_type="STOP_COMPLETED",
                entity_type="TripStop",
                entity_id=UUID(str(stop.id)),
                job_id=UUID(str(stop.job_id)) if stop.job_id else None,
                trip_id=UUID(str(stop.trip_id)),
                vehicle_id=UUID(str(trip.vehicle_id)),
                driver_id=UUID(str(trip.driver_id)),
                summary=f"Stop #{stop.sequence} '{stop.location_name}' marked Completed",
                payload={"stop_type": stop.stop_type, "sequence": stop.sequence}
            )

            # Event 3: DELIVERED (if job linked)
            if stop.job_id:
                audit.record_event(
                    event_type="DELIVERED",
                    entity_type="Job",
                    entity_id=UUID(str(stop.job_id)),
                    job_id=UUID(str(stop.job_id)),
                    trip_id=UUID(str(stop.trip_id)),
                    vehicle_id=UUID(str(trip.vehicle_id)),
                    driver_id=UUID(str(trip.driver_id)),
                    summary=f"Job payload successfully delivered to {req.receiver_name}",
                    payload={"receiver_name": req.receiver_name, "delivered_at": now.isoformat()}
                )
        except Exception:
            pass  # Non-blocking event logging

        return PODResponse(
            stop_id=UUID(str(stop.id)),
            trip_id=UUID(str(stop.trip_id)),
            job_id=UUID(str(stop.job_id)) if stop.job_id else None,
            stop_sequence=int(str(stop.sequence)),
            location_name=str(stop.location_name),
            stop_type=str(stop.stop_type),
            stop_status=str(stop.status),
            delivered_at=now,
            is_geofence_verified=is_geofence_valid,
            geo_distance_offset_meters=round(dist_meters, 1),
            proof_of_delivery=pod_payload,
            trip_completed=trip_completed
        )

    def get_proof_of_delivery(self, stop_id: UUID) -> PODResponse:
        """Fetch proof of delivery details for a completed trip stop."""
        stop = self.db.query(TripStop).filter(TripStop.id == stop_id).first()
        if not stop:
            raise NotFoundError(f"Trip stop with ID '{stop_id}' not found.")

        pod_raw = getattr(stop, 'proof_of_delivery', {}) or {}
        pod_data: Dict[str, Any] = dict(pod_raw) if isinstance(pod_raw, dict) else {}

        return PODResponse(
            stop_id=UUID(str(stop.id)),
            trip_id=UUID(str(stop.trip_id)),
            job_id=UUID(str(stop.job_id)) if stop.job_id else None,
            stop_sequence=int(str(stop.sequence)),
            location_name=str(stop.location_name),
            stop_type=str(stop.stop_type),
            stop_status=str(stop.status),
            delivered_at=datetime.fromisoformat(pod_data["delivered_at"]) if "delivered_at" in pod_data else datetime.now(),
            is_geofence_verified=pod_data.get("is_geofence_verified", True),
            geo_distance_offset_meters=pod_data.get("geo_distance_offset_meters", 0.0),
            proof_of_delivery=pod_data,
            trip_completed=(stop.trip.status == "Completed") if stop.trip else False
        )

    @staticmethod
    def _haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance in meters."""
        r = 6371000.0  # Radius of earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c
