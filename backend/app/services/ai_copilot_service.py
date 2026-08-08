"""
AI Fleet Copilot Service.
Intelligent conversational assistant querying telemetry, vehicle health, dispatch recommendations, and fleet analytics.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.models.trip import Trip
from app.models.driver import Driver
from app.schemas.ai_copilot import AICopilotQueryRequest, AICopilotQueryResponse
from app.services.analytics_service import AnalyticsService
from app.services.vehicle_recommendation_service import VehicleRecommendationService


class AICopilotService:
    """Conversational AI Copilot for natural language fleet queries."""

    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
        self.recommend_service = VehicleRecommendationService(db)

    def process_query(self, req: AICopilotQueryRequest) -> AICopilotQueryResponse:
        prompt_lower = req.prompt.lower()

        # Intent 1: Fleet Health & Scores
        if "health" in prompt_lower or "score" in prompt_lower or "condition" in prompt_lower:
            health_summary = self.analytics_service.get_enterprise_intelligence_summary()
            critical_count = sum(1 for h in health_summary.health_rankings if h.health_grade == "Critical")
            answer = (
                f"The overall fleet health score is {health_summary.overall_fleet_health_score}/100 "
                f"({health_summary.fleet_health_grade}). There are currently {critical_count} vehicles in Critical condition "
                f"and {health_summary.urgent_maintenance_forecasts_count} urgent predictive maintenance alerts."
            )
            return AICopilotQueryResponse(
                answer=answer,
                intent="FLEET_HEALTH",
                structured_data={
                    "overall_score": health_summary.overall_fleet_health_score,
                    "critical_vehicles": critical_count,
                },
                suggested_actions=[
                    {"label": "View Fleet Health", "url": "/analytics/fleet-health"},
                    {"label": "View Predictive Maintenance", "url": "/analytics/predictive-maintenance"}
                ]
            )

        # Intent 2: Fuel Theft / Anomalies
        elif "fuel" in prompt_lower or "theft" in prompt_lower or "drain" in prompt_lower:
            anomalies = self.analytics_service.detect_fuel_anomalies(days=30)
            if anomalies:
                answer = f"⚠️ Detected {len(anomalies)} critical fuel drain/theft anomalies in the last 30 days totaling {sum(a.fuel_loss_liters for a in anomalies):.1f} Liters."
            else:
                answer = "✅ No fuel drain or theft anomalies detected across the fleet in the past 30 days."
            return AICopilotQueryResponse(
                answer=answer,
                intent="FUEL_CHECK",
                structured_data={"anomalies_count": len(anomalies)},
                suggested_actions=[{"label": "View Fuel Anomalies", "url": "/analytics/fuel-anomalies"}]
            )

        # Intent 3: Vehicle & Dispatch Recommendation
        elif "recommend" in prompt_lower or "assign" in prompt_lower or "best vehicle" in prompt_lower:
            available_v = self.db.query(Vehicle).filter(Vehicle.status == "Available").count()
            answer = f"Found {available_v} available vehicles for dispatch. Use our multi-factor recommendation engine to auto-match capacity, driver hours, and health scores."
            return AICopilotQueryResponse(
                answer=answer,
                intent="RECOMMENDATION",
                structured_data={"available_vehicles": available_v},
                suggested_actions=[{"label": "Open Dispatch Board", "url": "/dispatch"}]
            )

        # General Fallback
        else:
            total_v = self.db.query(Vehicle).count()
            active_trips = self.db.query(Trip).filter(Trip.status == "Dispatched").count()
            answer = f"TransitOps AI Copilot monitoring {total_v} fleet vehicles. Currently {active_trips} trips are active in dispatch."
            return AICopilotQueryResponse(
                answer=answer,
                intent="GENERAL",
                structured_data={"total_vehicles": total_v, "active_trips": active_trips},
                suggested_actions=[{"label": "View Live Map", "url": "/fleet-map"}]
            )
