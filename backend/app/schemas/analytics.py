"""
Enterprise Intelligence & Analytics Pydantic Schemas.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FuelAnomalyAlert(BaseModel):
    """Schema for detected fuel drain/theft or abnormal consumption event."""
    vehicle_id: UUID
    registration_number: str
    anomaly_type: str  # e.g., "FUEL_DRAIN_THEFT", "ABNORMAL_CONSUMPTION", "REFUEL"
    severity: str      # "CRITICAL", "WARNING", "INFO"
    fuel_loss_liters: float
    time_span_minutes: float
    detected_at: datetime
    location: Dict[str, Optional[float]]
    summary: str


class VehicleHealthBreakdown(BaseModel):
    """Multi-factor Fleet Health Score (0-100) detail for a vehicle."""
    vehicle_id: UUID
    registration_number: str
    vehicle_name: str
    vehicle_type: str
    health_score: float = Field(..., ge=0.0, le=100.0)
    health_grade: str   # "Excellent", "Good", "Warning", "Critical"
    deductions: List[Dict[str, Any]]
    odometer_km: float
    overdue_maintenance_count: int
    dtc_fault_codes_count: int
    recent_speeding_alerts_count: int


class FleetTCOAnalytics(BaseModel):
    """Total Cost of Ownership ($/km) breakdown."""
    vehicle_id: Optional[UUID] = None
    registration_number: Optional[str] = None
    total_distance_km: float
    fuel_cost: float
    maintenance_cost: float
    expense_cost: float
    total_tco: float
    cost_per_km: float


class PredictiveWearItem(BaseModel):
    """Predictive component wear model item."""
    component: str  # e.g., "Engine Oil", "Brake Pads", "Tires", "Transmission Fluid"
    current_wear_percent: float = Field(..., ge=0.0, le=100.0)
    remaining_lifespan_km: float
    estimated_days_remaining: int
    recommended_action: str
    urgency: str  # "URGENT", "ATTENTION", "NORMAL"


class VehiclePredictiveMaintenanceForecast(BaseModel):
    """Predictive maintenance forecast for a vehicle."""
    vehicle_id: UUID
    registration_number: str
    avg_daily_km: float
    components: List[PredictiveWearItem]


class EnterpriseIntelligenceSummary(BaseModel):
    """Master Analytics Response."""
    overall_fleet_health_score: float
    fleet_health_grade: str
    total_active_vehicles: int
    fuel_anomalies_detected_30d: int
    total_fleet_tco: float
    avg_fleet_cost_per_km: float
    urgent_maintenance_forecasts_count: int
    health_rankings: List[VehicleHealthBreakdown]
    tco_breakdowns: List[FleetTCOAnalytics]
    fuel_anomalies: List[FuelAnomalyAlert]
    predictive_forecasts: List[VehiclePredictiveMaintenanceForecast]
