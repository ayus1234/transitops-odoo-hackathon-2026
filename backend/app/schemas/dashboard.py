"""
Dashboard and analytics schemas.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date
from uuid import UUID


# ============================================================
# Fleet & Driver Overviews
# ============================================================

class FleetOverview(BaseModel):
    total_vehicles: int
    active_vehicles: int
    vehicles_in_shop: int
    vehicles_on_trip: int
    retired_vehicles: int


class DriverOverview(BaseModel):
    total_drivers: int
    active_drivers: int
    drivers_on_trip: int
    available_drivers: int
    license_expiry_alerts: int


# ============================================================
# Core Analytics
# ============================================================

class TripAnalytics(BaseModel):
    total_trips: int
    active_trips: int
    completed_trips: int
    cancelled_trips: int
    average_trip_distance_km: float
    average_trip_cost: float


class MaintenanceAnalytics(BaseModel):
    pending_maintenance: int
    in_progress_maintenance: int
    completed_maintenance: int
    monthly_maintenance_cost: float


class FuelAnalytics(BaseModel):
    total_fuel_cost: float
    fuel_consumption_liters: float
    average_fuel_efficiency_kmpl: float
    fuel_cost_trend: List[Dict[str, Any]]  # e.g., [{"month": "2024-01", "cost": 1500.0}]


class ExpenseAnalytics(BaseModel):
    total_expenses: float
    expenses_by_category: Dict[str, float]
    monthly_expenses: float
    expense_trend: List[Dict[str, Any]]


# ============================================================
# Financial Summary
# ============================================================

class FinancialSummary(BaseModel):
    total_operational_cost: float
    fuel_cost: float
    maintenance_cost: float
    other_expenses: float


# ============================================================
# Alerts
# ============================================================

class AlertItem(BaseModel):
    id: UUID
    entity_name: str
    alert_type: str
    due_date: date
    days_remaining: int
    severity: str  # "Critical", "Warning", "Info"
    task: str | None = None
    status: str | None = None

class DashboardAlerts(BaseModel):
    maintenance_due: List[AlertItem]
    licenses_expiring: List[AlertItem]
    insurance_expiring: List[AlertItem]
    registration_expiring: List[AlertItem]


# ============================================================
# Dashboard Master Overview
# ============================================================

class DashboardOverview(BaseModel):
    fleet: FleetOverview
    drivers: DriverOverview
    trips: TripAnalytics
    financial: FinancialSummary
