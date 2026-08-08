"""
Google Maps Directions Routing Provider Adapter.
"""
import urllib.request
import urllib.parse
import json
from typing import List, Tuple, Optional, Dict, Any
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.haversine_provider import HaversineFallbackProvider


class GoogleMapsProvider(BaseRoutingProvider):
    """Google Maps Directions API Provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.fallback = HaversineFallbackProvider()

    @property
    def provider_name(self) -> str:
        return "Google Maps API"

    def calculate_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        average_speed_kmh: float = 60.0
    ) -> Dict[str, Any]:
        """Query Google Maps Directions API."""
        if not self.api_key:
            res = self.fallback.calculate_route(origin, destination, waypoints, average_speed_kmh)
            res["provider_used"] = "Google Maps (Fallback to Haversine — No Key Provided)"
            return res

        orig_str = f"{origin[0]},{origin[1]}"
        dest_str = f"{destination[0]},{destination[1]}"
        
        params = {
            "origin": orig_str,
            "destination": dest_str,
            "key": self.api_key
        }

        if waypoints:
            way_str = "|".join([f"{pt[0]},{pt[1]}" for pt in waypoints])
            params["waypoints"] = way_str

        url = f"https://maps.googleapis.com/maps/api/directions/json?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TransitOps-ERP/2.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if data.get("status") == "OK" and data.get("routes"):
                        route = data["routes"][0]
                        polyline = route.get("overview_polyline", {}).get("points", "")
                        
                        total_dist_meters = sum(leg["distance"]["value"] for leg in route.get("legs", []))
                        total_dur_seconds = sum(leg["duration"]["value"] for leg in route.get("legs", []))

                        legs = []
                        for idx, leg in enumerate(route.get("legs", [])):
                            legs.append({
                                "leg_index": idx,
                                "origin_name": leg.get("start_address", f"Point {idx}"),
                                "destination_name": leg.get("end_address", f"Point {idx+1}"),
                                "distance_km": round(leg["distance"]["value"] / 1000.0, 2),
                                "duration_minutes": round(leg["duration"]["value"] / 60.0, 1)
                            })

                        return {
                            "total_distance_km": round(total_dist_meters / 1000.0, 2),
                            "total_duration_minutes": round(total_dur_seconds / 60.0, 1),
                            "legs": legs,
                            "polyline_geometry": polyline
                        }
        except Exception:
            pass

        res = self.fallback.calculate_route(origin, destination, waypoints, average_speed_kmh)
        res["provider_used"] = "Google Maps (Fallback to Haversine)"
        return res
