"""
Unified Routing & Multi-Stop ETA Calculation Service.
"""
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.trip import Trip
from app.models.trip_stop import TripStop
from app.models.job import Job
from app.schemas.routing import (
    RouteCalculationRequest,
    RouteCalculationResponse,
    RouteLeg,
    MultiStopETAResponse,
    StopETA,
    CoordinateLocation
)
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.haversine_provider import HaversineFallbackProvider
from app.services.routing.osrm_provider import OSRMProvider
from app.services.routing.google_maps_provider import GoogleMapsProvider
from app.utils.exceptions import NotFoundError, BusinessLogicError


class RoutingService:
    """Routing & ETA Service orchestrating provider strategy."""

    def __init__(self, db: Session, provider: Optional[BaseRoutingProvider] = None):
        self.db = db
        if provider:
            self.provider = provider
        else:
            # Auto-select provider based on system settings
            google_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
            osrm_url = getattr(settings, 'OSRM_BASE_URL', "http://router.project-osrm.org")

            if google_key:
                self.provider = GoogleMapsProvider(api_key=google_key)
            elif osrm_url:
                self.provider = OSRMProvider(base_url=osrm_url)
            else:
                self.provider = HaversineFallbackProvider()

    def calculate_route(self, request: RouteCalculationRequest) -> RouteCalculationResponse:
        """Calculate route distance, duration, legs, and geometry polyline."""
        origin_pt = (request.origin.latitude, request.origin.longitude)
        dest_pt = (request.destination.latitude, request.destination.longitude)

        waypoints_pts = [
            (wp.latitude, wp.longitude) for wp in (request.waypoints or [])
        ]

        result = self.provider.calculate_route(
            origin=origin_pt,
            destination=dest_pt,
            waypoints=waypoints_pts,
            average_speed_kmh=request.average_speed_kmh or 60.0
        )

        legs = [
            RouteLeg(
                leg_index=leg["leg_index"],
                origin_name=leg["origin_name"],
                destination_name=leg["destination_name"],
                distance_km=leg["distance_km"],
                duration_minutes=leg["duration_minutes"]
            )
            for leg in result.get("legs", [])
        ]

        return RouteCalculationResponse(
            total_distance_km=result["total_distance_km"],
            total_duration_minutes=result["total_duration_minutes"],
            provider_used=result.get("provider_used", self.provider.provider_name),
            legs=legs,
            polyline_geometry=result.get("polyline_geometry")
        )

    def calculate_multi_stop_eta(
        self,
        trip_id: UUID,
        departure_time: Optional[datetime] = None
    ) -> MultiStopETAResponse:
        """
        Calculate stop-by-stop ETAs, update planned arrival/departure per stop,
        and update overall trip planned distance and arrival.
        """
        trip = self.db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise NotFoundError(f"Trip with ID '{trip_id}' not found.")

        stops = self.db.query(TripStop).filter(
            TripStop.trip_id == trip_id
        ).order_by(TripStop.sequence.asc()).all()

        if not stops:
            # Fallback if no explicit stops exist
            stops = self._synthesize_stops_from_trip(trip)

        # Baseline start time
        start_time = departure_time or trip.planned_departure or datetime.now()

        # Extract coordinates per stop (or generate fallback approximations if missing)
        coord_list: List[Tuple[float, float]] = []
        for stop in stops:
            lat = float(str(stop.latitude)) if stop.latitude is not None else None
            lng = float(str(stop.longitude)) if stop.longitude is not None else None

            if lat is None or lng is None:
                # Approximate from location name or default grid offset
                lat, lng = self._approximate_coords_for_stop(stop, trip)

            coord_list.append((lat, lng))

        origin_pt = coord_list[0]
        dest_pt = coord_list[-1]
        waypoint_pts = coord_list[1:-1] if len(coord_list) > 2 else []

        route_res = self.provider.calculate_route(
            origin=origin_pt,
            destination=dest_pt,
            waypoints=waypoint_pts
        )

        legs = route_res.get("legs", [])
        stop_eta_results: List[StopETA] = []

        current_time = start_time
        total_dist_km = 0.0

        for i, stop in enumerate(stops):
            if i == 0:
                # Origin stop
                dist_prev = 0.0
                travel_min = 0.0
                dwell_min = 20 if stop.stop_type in ["Origin", "Pickup"] else 10
                arrival = current_time
                departure = current_time + timedelta(minutes=dwell_min)
            else:
                leg_idx = i - 1
                if leg_idx < len(legs):
                    dist_prev = legs[leg_idx]["distance_km"]
                    travel_min = legs[leg_idx]["duration_minutes"]
                else:
                    dist_prev = 15.0
                    travel_min = 15.0

                current_time += timedelta(minutes=travel_min)
                arrival = current_time

                # Dwell time based on stop type
                dwell_min = 30 if stop.stop_type in ["Pickup", "Delivery"] else 15
                departure = arrival + timedelta(minutes=dwell_min)

            current_time = departure
            total_dist_km += dist_prev

            # Update DB TripStop model attributes
            setattr(stop, 'planned_arrival', arrival)
            setattr(stop, 'planned_departure', departure)
            setattr(stop, 'distance_from_prev_km', Decimal(str(round(dist_prev, 2))))
            setattr(stop, 'travel_time_from_prev_min', Decimal(str(round(travel_min, 1))))

            stop_eta_results.append(StopETA(
                stop_id=UUID(str(stop.id)),
                sequence=int(str(stop.sequence)),
                location_name=str(stop.location_name),
                stop_type=str(stop.stop_type),
                planned_arrival=arrival,
                planned_departure=departure,
                distance_from_prev_km=round(dist_prev, 2),
                travel_time_from_prev_min=round(travel_min, 1),
                dwell_time_minutes=dwell_min
            ))

        # Update Trip master record
        setattr(trip, 'planned_distance_km', Decimal(str(round(total_dist_km, 2))))
        setattr(trip, 'planned_arrival', stop_eta_results[-1].planned_arrival if stop_eta_results else start_time)

        self.db.commit()

        return MultiStopETAResponse(
            trip_id=UUID(str(trip.id)),
            total_distance_km=round(total_dist_km, 2),
            total_duration_minutes=round(route_res["total_duration_minutes"], 1),
            provider_used=route_res.get("provider_used", self.provider.provider_name),
            stops=stop_eta_results,
            route_geometry=route_res.get("polyline_geometry")
        )

    def _synthesize_stops_from_trip(self, trip: Trip) -> List[TripStop]:
        """Create baseline TripStops for single-leg trip if none exist."""
        origin_stop = TripStop(
            trip_id=trip.id,
            sequence=1,
            location_name=trip.source,
            stop_type="Origin",
            status="Pending"
        )
        dest_stop = TripStop(
            trip_id=trip.id,
            sequence=2,
            location_name=trip.destination,
            stop_type="Destination",
            status="Pending"
        )
        self.db.add(origin_stop)
        self.db.add(dest_stop)
        self.db.commit()
        return [origin_stop, dest_stop]

    @staticmethod
    def _approximate_coords_for_stop(stop: TripStop, trip: Trip) -> Tuple[float, float]:
        """Generate fallback coordinates for stops based on sequence or location names."""
        loc = (stop.location_name or "").lower()
        if "mumbai" in loc or "bkc" in loc:
            return 19.0760, 72.8777
        if "pune" in loc:
            return 18.5204, 73.8567
        if "delhi" in loc:
            return 28.6139, 77.2090
        if "jaipur" in loc:
            return 26.9124, 75.7873

        # Default grid offset
        seq = int(str(stop.sequence))
        return 19.0760 + (seq * 0.15), 72.8777 + (seq * 0.20)
