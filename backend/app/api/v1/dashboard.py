"""
Dashboard and Analytics API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.dashboard import (
    FleetOverview,
    DriverOverview,
    TripAnalytics,
    MaintenanceAnalytics,
    FuelAnalytics,
    ExpenseAnalytics,
    FinancialSummary,
    DashboardAlerts,
    DashboardOverview
)
from app.schemas.common import SuccessResponse
from app.services.dashboard_service import DashboardService


router = APIRouter()


@router.get("/overview", response_model=dict)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get master overview metrics for the main dashboard.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_master_overview()
    return {"success": True, "data": DashboardOverview.model_validate(data)}


@router.get("/fleet", response_model=dict)
def get_fleet_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get fleet overview metrics.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_fleet_overview()
    return {"success": True, "data": FleetOverview.model_validate(data)}


@router.get("/trips", response_model=dict)
def get_trip_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get trip analytics metrics.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_trip_analytics()
    return {"success": True, "data": TripAnalytics.model_validate(data)}


@router.get("/maintenance", response_model=dict)
def get_maintenance_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get maintenance analytics metrics.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_maintenance_analytics()
    return {"success": True, "data": MaintenanceAnalytics.model_validate(data)}


@router.get("/fuel", response_model=dict)
def get_fuel_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get fuel analytics metrics.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_fuel_analytics()
    return {"success": True, "data": FuelAnalytics.model_validate(data)}


@router.get("/expenses", response_model=dict)
def get_expense_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get expense analytics metrics.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_expense_analytics()
    return {"success": True, "data": ExpenseAnalytics.model_validate(data)}


@router.get("/financial-summary", response_model=dict)
def get_financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get financial summary metrics.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_financial_summary()
    return {"success": True, "data": FinancialSummary.model_validate(data)}


@router.get("/alerts", response_model=dict)
def get_dashboard_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    """
    Get dashboard alerts for expiring/due items.
    Permissions: dashboard:read
    """
    service = DashboardService(db)
    data = service.get_alerts()
    return {"success": True, "data": DashboardAlerts.model_validate(data)}
