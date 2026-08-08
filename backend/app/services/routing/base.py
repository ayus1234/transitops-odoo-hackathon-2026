"""
Abstract Base Class for Routing & Navigation Providers.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any


class BaseRoutingProvider(ABC):
    """Abstract Routing Provider Interface."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique provider name (e.g. 'Haversine', 'OSRM', 'GoogleMaps')."""
        pass

    @abstractmethod
    def calculate_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        average_speed_kmh: float = 60.0
    ) -> Dict[str, Any]:
        """
        Calculate route distance, duration, leg breakdowns, and geometry polyline.
        
        Returns:
            Dict containing:
                - total_distance_km (float)
                - total_duration_minutes (float)
                - legs (List[Dict])
                - polyline_geometry (str)
        """
        pass
