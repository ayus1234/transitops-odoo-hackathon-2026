"""
Enterprise Intelligence & Analytics API Router.
Exposes endpoints for fuel theft detection, Fleet Health Scores (0-100), TCO ($/km) breakdowns, and predictive wear models.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User
from app.schemas.analytics import (
    EnterpriseIntelligenceSummary,
    FuelAnomalyAlert,
    VehicleHealthBreakdown,
    FleetTCOAnalytics,
    VehiclePredictiveMaintenanceForecast,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Enterprise Intelligence & Analytics"])


@router.get("/intelligence", response_model=EnterpriseIntelligenceSummary)
def get_enterprise_intelligence(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    """Get master Enterprise Intelligence summary dashboard."""
    service = AnalyticsService(db)
    return service.get_enterprise_intelligence_summary()


@router.get("/fuel-anomalies", response_model=List[FuelAnomalyAlert])
def get_fuel_anomalies(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("fuel", "read"))
):
    """Detect rapid fuel drain/theft and consumption anomalies."""
    service = AnalyticsService(db)
    return service.detect_fuel_anomalies(days=days)


@router.get("/fleet-health", response_model=List[VehicleHealthBreakdown])
def get_fleet_health_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vehicles", "read"))
):
    """Get 0-100 multi-factor Fleet Health Scores for all vehicles."""
    service = AnalyticsService(db)
    return service.calculate_fleet_health_scores()


@router.get("/tco", response_model=List[FleetTCOAnalytics])
def get_tco_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    """Get Total Cost of Ownership ($/km) analytics across the fleet."""
    service = AnalyticsService(db)
    return service.calculate_tco_analytics()


@router.get("/predictive-maintenance", response_model=List[VehiclePredictiveMaintenanceForecast])
def get_predictive_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get component wear forecasts and predictive maintenance timelines."""
    service = AnalyticsService(db)
    return service.forecast_predictive_maintenance()
