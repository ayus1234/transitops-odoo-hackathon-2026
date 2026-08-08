"""
Fleet Payroll & Driver Hours Pydantic Schemas.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
from pydantic import BaseModel, Field


class DriverPayrollCalculation(BaseModel):
    """Driver payroll statement schema."""
    driver_id: UUID
    driver_name: str
    license_number: str
    period_start: date
    period_end: date
    completed_trips_count: int
    total_distance_km: float
    base_pay: float
    per_km_bonus: float
    safety_bonus: float
    total_gross_pay: float
    status: str  # "Draft", "Approved", "Paid"


class DriverPayrollSummary(BaseModel):
    """Fleet-wide payroll summary payload."""
    period_start: date
    period_end: date
    total_drivers_paid: int
    total_payroll_cost: float
    driver_statements: List[DriverPayrollCalculation]
