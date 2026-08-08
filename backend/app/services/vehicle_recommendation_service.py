"""
Vehicle & Driver Intelligent Recommendation Engine.
Calculates multi-factor weighted match scores for assigning vehicles/drivers to customer jobs.
"""
import math
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.maintenance import Maintenance
from app.models.user import User
from app.schemas.vehicle_recommendation import (
    VehicleRecommendationResponse,
    VehicleRecommendationItem,
    MatchScoreBreakdown
)
from app.utils.exceptions import NotFoundError, BusinessLogicError


class VehicleRecommendationService:
    """Intelligent vehicle-job ranking service."""

    def __init__(self, db: Session):
        self.db = db

    def recommend_vehicles_for_job(
        self,
        job_id: UUID,
        top_n: int = 5
    ) -> VehicleRecommendationResponse:
        """
        Rank available fleet vehicles for a given job using multi-factor evaluation.
        """
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise NotFoundError(f"Job with ID '{job_id}' not found.")

        # Query candidate vehicles (Available or Acquired status)
        candidate_vehicles = self.db.query(Vehicle).filter(
            Vehicle.status.in_(["Available", "Acquired"])
        ).all()

        # Query available drivers
        available_drivers = self.db.query(Driver).filter(
            Driver.status == "Available"
        ).all()

        cargo_weight = float(str(job.cargo_weight_kg)) if job.cargo_weight_kg is not None else 0.0

        recommendations: List[VehicleRecommendationItem] = []

        for vehicle in candidate_vehicles:
            capacity_kg = float(str(vehicle.capacity_kg)) if vehicle.capacity_kg is not None else 0.0

            # Disqualify if cargo exceeds payload capacity
            if cargo_weight > capacity_kg and capacity_kg > 0:
                continue

            # 1. Capacity Fit Score (35%)
            cap_score, cap_reason = self._score_capacity_fit(cargo_weight, capacity_kg)

            # 2. Location Proximity Score (30%)
            prox_score, est_dist_km, prox_reason = self._score_location_proximity(job, vehicle)

            # 3. Fleet Health & Compliance Score (20%)
            health_score, health_reason = self._score_fleet_health(vehicle)

            # 4. Driver Suitability Score (15%)
            suggested_driver, driver_score, driver_reason = self._find_best_driver_for_vehicle(available_drivers)

            # Weighted overall calculation
            overall_score = round(
                0.35 * cap_score +
                0.30 * prox_score +
                0.20 * health_score +
                0.15 * driver_score,
                1
            )

            # Compile match reasons
            match_reasons = [cap_reason, prox_reason, health_reason, driver_reason]

            driver_id = None
            driver_name = None
            if suggested_driver:
                driver_id = UUID(str(suggested_driver.id))
                user = self.db.query(User).filter(User.id == suggested_driver.user_id).first()
                if user:
                    driver_name = f"{user.first_name} {user.last_name}".strip()
                else:
                    driver_name = f"Driver #{suggested_driver.license_number}"

            recommendations.append(VehicleRecommendationItem(
                vehicle_id=UUID(str(vehicle.id)),
                vehicle_name=vehicle.vehicle_name,
                registration_number=vehicle.registration_number,
                vehicle_type=vehicle.vehicle_type,
                capacity_kg=capacity_kg,
                current_status=vehicle.status,
                overall_match_score=overall_score,
                score_breakdown=MatchScoreBreakdown(
                    capacity_score=round(cap_score, 1),
                    proximity_score=round(prox_score, 1),
                    health_score=round(health_score, 1),
                    driver_score=round(driver_score, 1)
                ),
                match_reasons=match_reasons,
                suggested_driver_id=driver_id,
                suggested_driver_name=driver_name,
                estimated_proximity_km=round(est_dist_km, 1) if est_dist_km is not None else None
            ))

        # Sort recommendations descending by overall match score
        recommendations.sort(key=lambda x: x.overall_match_score, reverse=True)

        # Slice to top_n
        top_recommendations = recommendations[:top_n]

        return VehicleRecommendationResponse(
            job_id=UUID(str(job.id)),
            job_number=job.job_number,
            cargo_weight_kg=cargo_weight,
            total_candidates_evaluated=len(candidate_vehicles),
            recommendations=top_recommendations
        )

    def _score_capacity_fit(self, cargo_kg: float, capacity_kg: float) -> Tuple[float, str]:
        """Calculate payload capacity fill score (35% weight)."""
        if capacity_kg <= 0:
            return 50.0, "Vehicle capacity not specified"

        fill_ratio = cargo_kg / capacity_kg

        if fill_ratio > 1.0:
            return 0.0, f"Over capacity (Cargo {cargo_kg:.0f} kg > Limit {capacity_kg:.0f} kg)"

        if 0.70 <= fill_ratio <= 0.95:
            return 100.0, f"Optimal payload utilization ({fill_ratio * 100:.1f}% capacity used)"
        
        if 0.50 <= fill_ratio < 0.70:
            score = 80.0 + ((fill_ratio - 0.50) / 0.20) * 20.0
            return score, f"Good payload fit ({fill_ratio * 100:.1f}% capacity used)"
        
        if fill_ratio < 0.50:
            score = max(30.0, (fill_ratio / 0.50) * 80.0)
            return score, f"Sub-optimal payload utilization ({fill_ratio * 100:.1f}% capacity — vehicle is oversized)"

        # 0.95 < fill_ratio <= 1.00
        score = 100.0 - ((fill_ratio - 0.95) / 0.05) * 20.0
        return score, f"Tight payload fit ({fill_ratio * 100:.1f}% capacity used)"

    def _score_location_proximity(
        self,
        job: Job,
        vehicle: Vehicle
    ) -> Tuple[float, Optional[float], str]:
        """Calculate proximity score based on coordinates or baseline (30% weight)."""
        job_lat = job.pickup_latitude
        job_lng = job.pickup_longitude

        # Check vehicle coordinates or fallback
        veh_lat = getattr(vehicle, 'current_latitude', None)
        veh_lng = getattr(vehicle, 'current_longitude', None)

        if job_lat is not None and job_lng is not None and veh_lat is not None and veh_lng is not None:
            dist_km = self._haversine_distance(
                float(job_lat), float(job_lng),
                float(veh_lat), float(veh_lng)
            )
        else:
            # Baseline estimation: same city / location string heuristic
            job_pickup = (job.pickup_address or "").lower()
            veh_loc = (getattr(vehicle, 'assigned_depot', None) or getattr(vehicle, 'current_location', None) or "").lower()

            if job_pickup and veh_loc and any(word in job_pickup for word in veh_loc.split()):
                dist_km = 8.0
            else:
                dist_km = 25.0

        if dist_km <= 10.0:
            score = 100.0
            reason = f"Proximity: Nearby ({dist_km:.1f} km from pickup)"
        elif dist_km <= 50.0:
            score = 100.0 - ((dist_km - 10.0) / 40.0) * 40.0
            reason = f"Proximity: Moderate distance ({dist_km:.1f} km from pickup)"
        elif dist_km <= 150.0:
            score = 60.0 - ((dist_km - 50.0) / 100.0) * 50.0
            reason = f"Proximity: Distant ({dist_km:.1f} km from pickup)"
        else:
            score = 10.0
            reason = f"Proximity: Long deadhead distance ({dist_km:.1f} km)"

        return score, dist_km, reason

    def _score_fleet_health(self, vehicle: Vehicle) -> Tuple[float, str]:
        """Calculate health score based on open maintenance logs & document status (20% weight)."""
        open_maintenance = self.db.query(Maintenance).filter(
            Maintenance.vehicle_id == vehicle.id,
            Maintenance.status.in_(["Pending", "Approved", "In Progress"])
        ).all()

        health_score = 100.0
        reasons = []

        if open_maintenance:
            for maint in open_maintenance:
                prio = (getattr(maint, 'priority', '') or '').lower()
                if prio in ['critical', 'high']:
                    health_score -= 40.0
                    reasons.append(f"Open High-Priority Maintenance #{maint.maintenance_number}")
                else:
                    health_score -= 15.0
                    reasons.append(f"Open Maintenance #{maint.maintenance_number}")

        health_score = max(0.0, health_score)

        if health_score >= 90.0:
            reason = "Vehicle health & maintenance status excellent"
        else:
            reason = f"Health warnings: {', '.join(reasons)}"

        return health_score, reason

    def _find_best_driver_for_vehicle(
        self,
        available_drivers: List[Driver]
    ) -> Tuple[Optional[Driver], float, str]:
        """Find best available driver for vehicle and calculate driver score (15% weight)."""
        if not available_drivers:
            return None, 40.0, "No available drivers currently in pool"

        today = date.today()
        eligible_drivers = []

        for d in available_drivers:
            score = 100.0
            reasons = []

            # Check license expiry
            if d.license_expiry_date and d.license_expiry_date < today:
                score -= 60.0
                reasons.append("License expired")

            # Check medical fitness expiry
            if getattr(d, 'medical_fitness_expiry', None) is not None:
                if getattr(d, 'medical_fitness_expiry') < today:
                    score -= 30.0
                    reasons.append("Medical expired")

            eligible_drivers.append((d, max(0.0, score), reasons))

        # Sort eligible drivers by score descending
        eligible_drivers.sort(key=lambda x: x[1], reverse=True)

        best_driver, best_score, reasons = eligible_drivers[0]

        if best_score >= 90.0:
            reason_str = f"Available compliant driver matched (License #{best_driver.license_number})"
        else:
            reason_str = f"Driver match warning: {', '.join(reasons)}"

        return best_driver, best_score, reason_str

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two points in km."""
        r = 6371.0  # Earth's radius in kilometers

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        return r * c
