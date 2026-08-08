"""
OSRM Routing Provider Adapter.
"""
import urllib.request
import json
from typing import List, Tuple, Optional, Dict, Any
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.haversine_provider import HaversineFallbackProvider


class OSRMProvider(BaseRoutingProvider):
    """OSRM Open Source Routing Machine Provider."""

    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        self.base_url = base_url.rstrip("/")
        self.fallback = HaversineFallbackProvider()

    @property
    def provider_name(self) -> str:
        return "OSRM Engine"

    def calculate_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        average_speed_kmh: float = 60.0
    ) -> Dict[str, Any]:
        """Query OSRM API for real road routing."""
        points = [origin] + (waypoints or []) + [destination]
        # OSRM expects coordinates in lon,lat format
        coord_str = ";".join([f"{pt[1]},{pt[0]}" for pt in points])
        url = f"{self.base_url}/route/v1/driving/{coord_str}?overview=full&steps=true"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TransitOps-ERP/2.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("code") == "Ok" and data.get("routes"):
                        route = data["routes"][0]
                        total_dist_km = route["distance"] / 1000.0
                        total_dur_min = route["duration"] / 60.0
                        polyline = route.get("geometry", "")

                        legs = []
                        for idx, leg in enumerate(route.get("legs", [])):
                            legs.append({
                                "leg_index": idx,
                                "origin_name": f"Waypoint {idx}" if idx > 0 else "Origin",
                                "destination_name": f"Waypoint {idx+1}" if idx + 1 < len(points) - 1 else "Destination",
                                "distance_km": round(leg["distance"] / 1000.0, 2),
                                "duration_minutes": round(leg["duration"] / 60.0, 1)
                            })

                        return {
                            "total_distance_km": round(total_dist_km, 2),
                            "total_duration_minutes": round(total_dur_min, 1),
                            "legs": legs,
                            "polyline_geometry": polyline
                        }
        except Exception:
            pass  # Fall back gracefully

        # Fallback to Haversine if external OSRM call is unreachable or fails
        fallback_res = self.fallback.calculate_route(origin, destination, waypoints, average_speed_kmh)
        fallback_res["provider_used"] = f"{self.provider_name} (Fallback to Haversine)"
        return fallback_res
