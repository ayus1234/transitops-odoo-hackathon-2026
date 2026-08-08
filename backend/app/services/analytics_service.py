"""
Enterprise Intelligence & Analytics Service.
Includes fuel theft detection algorithms, multi-factor Fleet Health Score (0-100), TCO ($/km) calculation, and predictive wear forecasting.
"""
import math
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vehicle import Vehicle
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.models.telemetry import VehicleTelemetryLog
from app.models.audit_event import AuditEvent
from app.schemas.analytics import (
    FuelAnomalyAlert,
    VehicleHealthBreakdown,
    FleetTCOAnalytics,
    PredictiveWearItem,
    VehiclePredictiveMaintenanceForecast,
    EnterpriseIntelligenceSummary,
)


class AnalyticsService:
    """Service providing advanced analytics, fuel anomaly detection, TCO modeling, and predictive wear forecasting."""

    DEFAULT_TANK_CAPACITY_LITERS = 300.0
    OIL_CHANGE_INTERVAL_KM = 10000.0
    BRAKE_PAD_INTERVAL_KM = 40000.0
    TIRE_REPLACEMENT_INTERVAL_KM = 60000.0
    TRANSMISSION_FLUID_INTERVAL_KM = 80000.0

    def __init__(self, db: Session):
        self.db = db

    def get_enterprise_intelligence_summary(self) -> EnterpriseIntelligenceSummary:
        """Master aggregator for enterprise intelligence dashboard."""
        health_rankings = self.calculate_fleet_health_scores()
        tco_breakdowns = self.calculate_tco_analytics()
        fuel_anomalies = self.detect_fuel_anomalies(days=30)
        predictive_forecasts = self.forecast_predictive_maintenance()

        total_vehicles = len(health_rankings)
        avg_health = (
            sum(h.health_score for h in health_rankings) / float(total_vehicles)
            if total_vehicles > 0 else 100.0
        )

        fleet_grade = (
            "Excellent" if avg_health >= 90 else
            "Good" if avg_health >= 75 else
            "Warning" if avg_health >= 50 else "Critical"
        )

        total_tco = sum(t.total_tco for t in tco_breakdowns)
        total_km = sum(t.total_distance_km for t in tco_breakdowns)
        avg_cost_per_km = (total_tco / total_km) if total_km > 0 else 0.0

        urgent_forecasts_count = sum(
            1 for f in predictive_forecasts
            if any(item.urgency == "URGENT" for item in f.components)
        )

        return EnterpriseIntelligenceSummary(
            overall_fleet_health_score=round(avg_health, 1),
            fleet_health_grade=fleet_grade,
            total_active_vehicles=total_vehicles,
            fuel_anomalies_detected_30d=len(fuel_anomalies),
            total_fleet_tco=round(total_tco, 2),
            avg_fleet_cost_per_km=round(avg_cost_per_km, 3),
            urgent_maintenance_forecasts_count=urgent_forecasts_count,
            health_rankings=health_rankings,
            tco_breakdowns=tco_breakdowns,
            fuel_anomalies=fuel_anomalies,
            predictive_forecasts=predictive_forecasts,
        )

    def detect_fuel_anomalies(self, days: int = 30) -> List[FuelAnomalyAlert]:
        """Detect rapid fuel level drops (fuel drain/theft) from telemetry logs."""
        anomalies: List[FuelAnomalyAlert] = []
        cutoff = datetime.now() - timedelta(days=days)

        vehicles = self.db.query(Vehicle).all()

        for v in vehicles:
            logs = self.db.query(VehicleTelemetryLog).filter(
                VehicleTelemetryLog.vehicle_id == v.id,
                VehicleTelemetryLog.timestamp >= cutoff,
                VehicleTelemetryLog.fuel_level_percent.isnot(None)
            ).order_by(VehicleTelemetryLog.timestamp.asc()).all()

            if len(logs) < 2:
                continue

            for i in range(1, len(logs)):
                prev = logs[i - 1]
                curr = logs[i]

                prev_fuel = getattr(prev, "fuel_level_percent", None)
                curr_fuel = getattr(curr, "fuel_level_percent", None)

                if prev_fuel is None or curr_fuel is None:
                    continue

                drop_percent = float(prev_fuel) - float(curr_fuel)
                dt_minutes = (curr.timestamp - prev.timestamp).total_seconds() / 60.0

                # Detect sudden drop > 15% in less than 30 minutes while speed is low (<10 km/h)
                if drop_percent >= 15.0 and 0.5 <= dt_minutes <= 30.0 and curr.speed_kmh < 10.0:
                    loss_liters = (drop_percent / 100.0) * self.DEFAULT_TANK_CAPACITY_LITERS
                    anomalies.append(FuelAnomalyAlert(
                        vehicle_id=UUID(str(v.id)),
                        registration_number=getattr(v, "registration_number", ""),
                        anomaly_type="FUEL_DRAIN_THEFT",
                        severity="CRITICAL",
                        fuel_loss_liters=round(loss_liters, 1),
                        time_span_minutes=round(dt_minutes, 1),
                        detected_at=getattr(curr, "timestamp", datetime.now()),
                        location={
                            "latitude": float(str(curr.latitude)) if curr.latitude else None,
                            "longitude": float(str(curr.longitude)) if curr.longitude else None,
                        },
                        summary=f"Critical fuel drop of {drop_percent:.1f}% ({loss_liters:.1f}L) detected in {dt_minutes:.1f} minutes on vehicle {v.registration_number}"
                    ))

        return anomalies

    def calculate_fleet_health_scores(self) -> List[VehicleHealthBreakdown]:
        """Compute multi-factor 0-100 Fleet Health Scores for all vehicles."""
        results: List[VehicleHealthBreakdown] = []
        vehicles = self.db.query(Vehicle).all()

        for v in vehicles:
            score = 100.0
            deductions: List[Dict[str, Any]] = []

            # 1. Maintenance Status Deductions
            overdue_maint = self.db.query(Maintenance).filter(
                Maintenance.vehicle_id == v.id,
                Maintenance.scheduled_date < date.today(),
                Maintenance.status != "Completed"
            ).count()

            if overdue_maint > 0:
                pts = min(overdue_maint * 15.0, 45.0)
                score -= pts
                deductions.append({"factor": "Overdue Maintenance", "points": pts, "reason": f"{overdue_maint} active/overdue maintenance work orders"})

            # 2. Vehicle Age / Odometer Deductions
            odom = float(str(v.current_odometer_km)) if v.current_odometer_km else 0.0
            if odom > 200000.0:
                score -= 15.0
                deductions.append({"factor": "High Odometer Wear", "points": 15.0, "reason": f"Odometer is {odom:,.0f} km (>200,000 km)"})
            elif odom > 100000.0:
                score -= 8.0
                deductions.append({"factor": "Moderate Odometer Wear", "points": 8.0, "reason": f"Odometer is {odom:,.0f} km (>100,000 km)"})

            # 3. Speeding & Safety Audit Event Deductions (last 30 days)
            cutoff_30d = datetime.now() - timedelta(days=30)
            speeding_events = self.db.query(AuditEvent).filter(
                AuditEvent.vehicle_id == v.id,
                AuditEvent.event_type == "SPEEDING_ALERT",
                AuditEvent.created_at >= cutoff_30d
            ).count()

            if speeding_events > 0:
                pts = min(speeding_events * 5.0, 20.0)
                score -= pts
                deductions.append({"factor": "Speeding Violations", "points": pts, "reason": f"{speeding_events} speeding alerts in past 30 days"})

            # Clamp score between 0 and 100
            score = max(0.0, min(100.0, score))
            grade = (
                "Excellent" if score >= 90 else
                "Good" if score >= 75 else
                "Warning" if score >= 50 else "Critical"
            )

            results.append(VehicleHealthBreakdown(
                vehicle_id=UUID(str(v.id)),
                registration_number=getattr(v, "registration_number", ""),
                vehicle_name=getattr(v, "vehicle_name", ""),
                vehicle_type=getattr(v, "vehicle_type", ""),
                health_score=round(score, 1),
                health_grade=grade,
                deductions=deductions,
                odometer_km=round(odom, 1),
                overdue_maintenance_count=overdue_maint,
                dtc_fault_codes_count=0,
                recent_speeding_alerts_count=speeding_events,
            ))

        return results

    def calculate_tco_analytics(self) -> List[FleetTCOAnalytics]:
        """Calculate Total Cost of Ownership ($/km) for all vehicles."""
        results: List[FleetTCOAnalytics] = []
        vehicles = self.db.query(Vehicle).all()

        for v in vehicles:
            # 1. Total Fuel Expenses
            fuel_total = self.db.query(func.sum(Fuel.total_cost)).filter(Fuel.vehicle_id == v.id).scalar() or Decimal("0.0")
            
            # 2. Total Maintenance Costs
            maint_total = self.db.query(func.sum(Maintenance.actual_cost)).filter(Maintenance.vehicle_id == v.id).scalar() or Decimal("0.0")

            # 3. Total Trip Expenses
            exp_total = self.db.query(func.sum(Expense.amount)).filter(Expense.vehicle_id == v.id).scalar() or Decimal("0.0")

            total_tco = float(fuel_total) + float(maint_total) + float(exp_total)
            odom = float(str(v.current_odometer_km)) if v.current_odometer_km else 1.0
            dist_km = max(odom, 1.0)
            cost_per_km = total_tco / dist_km

            results.append(FleetTCOAnalytics(
                vehicle_id=UUID(str(v.id)),
                registration_number=getattr(v, "registration_number", ""),
                total_distance_km=round(dist_km, 1),
                fuel_cost=round(float(fuel_total), 2),
                maintenance_cost=round(float(maint_total), 2),
                expense_cost=round(float(exp_total), 2),
                total_tco=round(total_tco, 2),
                cost_per_km=round(cost_per_km, 3),
            ))

        return results

    def forecast_predictive_maintenance(self) -> List[VehiclePredictiveMaintenanceForecast]:
        """Predict component wear percentages and remaining lifespan in days/km."""
        results: List[VehiclePredictiveMaintenanceForecast] = []
        vehicles = self.db.query(Vehicle).all()

        for v in vehicles:
            odom = float(str(v.current_odometer_km)) if v.current_odometer_km else 0.0
            avg_daily_km = 120.0  # Estimated average daily fleet usage

            components: List[PredictiveWearItem] = []

            # 1. Engine Oil (10,000 km cycle)
            oil_used = odom % self.OIL_CHANGE_INTERVAL_KM
            oil_wear = (oil_used / self.OIL_CHANGE_INTERVAL_KM) * 100.0
            oil_rem_km = self.OIL_CHANGE_INTERVAL_KM - oil_used
            oil_days = int(oil_rem_km / avg_daily_km)
            oil_urgency = "URGENT" if oil_wear >= 90.0 else "ATTENTION" if oil_wear >= 75.0 else "NORMAL"

            components.append(PredictiveWearItem(
                component="Engine Oil & Filter",
                current_wear_percent=round(oil_wear, 1),
                remaining_lifespan_km=round(oil_rem_km, 1),
                estimated_days_remaining=oil_days,
                recommended_action="Schedule oil and filter service" if oil_wear >= 75.0 else "Routine inspection",
                urgency=oil_urgency,
            ))

            # 2. Brake Pads (40,000 km cycle)
            brake_used = odom % self.BRAKE_PAD_INTERVAL_KM
            brake_wear = (brake_used / self.BRAKE_PAD_INTERVAL_KM) * 100.0
            brake_rem_km = self.BRAKE_PAD_INTERVAL_KM - brake_used
            brake_days = int(brake_rem_km / avg_daily_km)
            brake_urgency = "URGENT" if brake_wear >= 90.0 else "ATTENTION" if brake_wear >= 75.0 else "NORMAL"

            components.append(PredictiveWearItem(
                component="Brake Pads & Rotors",
                current_wear_percent=round(brake_wear, 1),
                remaining_lifespan_km=round(brake_rem_km, 1),
                estimated_days_remaining=brake_days,
                recommended_action="Inspect pad thickness & replace if <3mm" if brake_wear >= 75.0 else "Normal wear",
                urgency=brake_urgency,
            ))

            # 3. Tires (60,000 km cycle)
            tire_used = odom % self.TIRE_REPLACEMENT_INTERVAL_KM
            tire_wear = (tire_used / self.TIRE_REPLACEMENT_INTERVAL_KM) * 100.0
            tire_rem_km = self.TIRE_REPLACEMENT_INTERVAL_KM - tire_used
            tire_days = int(tire_rem_km / avg_daily_km)
            tire_urgency = "URGENT" if tire_wear >= 90.0 else "ATTENTION" if tire_wear >= 75.0 else "NORMAL"

            components.append(PredictiveWearItem(
                component="Tires & Alignment",
                current_wear_percent=round(tire_wear, 1),
                remaining_lifespan_km=round(tire_rem_km, 1),
                estimated_days_remaining=tire_days,
                recommended_action="Tire rotation and tread depth check" if tire_wear >= 75.0 else "Normal wear",
                urgency=tire_urgency,
            ))

            results.append(VehiclePredictiveMaintenanceForecast(
                vehicle_id=UUID(str(v.id)),
                registration_number=getattr(v, "registration_number", ""),
                avg_daily_km=avg_daily_km,
                components=components,
            ))

        return results
