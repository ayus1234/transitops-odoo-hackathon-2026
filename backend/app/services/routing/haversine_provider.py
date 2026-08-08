"""
Haversine Fallback Routing Provider.
Computes great-circle distance with road winding factor and speed heuristics.
"""
import math
from typing import List, Tuple, Optional, Dict, Any
from app.services.routing.base import BaseRoutingProvider


class HaversineFallbackProvider(BaseRoutingProvider):
    """Zero-dependency Haversine & speed heuristic routing provider."""

    ROAD_WINDING_FACTOR = 1.25  # Accounts for real road network curvature vs straight line

    @property
    def provider_name(self) -> str:
        return "Haversine Heuristic"

    def calculate_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        average_speed_kmh: float = 60.0
    ) -> Dict[str, Any]:
        """Calculate route legs and cumulative distance/duration."""
        points = [origin] + (waypoints or []) + [destination]
        legs = []
        total_dist_km = 0.0
        total_dur_min = 0.0

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]

            straight_dist = self._haversine(p1[0], p1[1], p2[0], p2[1])
            road_dist = straight_dist * self.ROAD_WINDING_FACTOR
            duration_min = (road_dist / max(10.0, average_speed_kmh)) * 60.0

            legs.append({
                "leg_index": i,
                "origin_name": f"Waypoint {i}" if i > 0 else "Origin",
                "destination_name": f"Waypoint {i+1}" if i + 1 < len(points) - 1 else "Destination",
                "distance_km": round(road_dist, 2),
                "duration_minutes": round(duration_min, 1)
            })

            total_dist_km += road_dist
            total_dur_min += duration_min

        # Simple polyline representation (lat,lng string sequence)
        poly = ";".join([f"{pt[0]:.6f},{pt[1]:.6f}" for pt in points])

        return {
            "total_distance_km": round(total_dist_km, 2),
            "total_duration_minutes": round(total_dur_min, 1),
            "legs": legs,
            "polyline_geometry": poly
        }

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in kilometers."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c
