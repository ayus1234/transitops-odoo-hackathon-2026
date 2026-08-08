"""
Fleet Payroll API Router.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.core.database import get_db
from app.api.deps import PermissionChecker
from app.models.user import User
from app.schemas.payroll import DriverPayrollSummary
from app.services.payroll_service import PayrollService

router = APIRouter(prefix="/payroll", tags=["Fleet Payroll & Driver Pay"])


@router.get("/drivers", response_model=DriverPayrollSummary)
def get_fleet_payroll(
    period_start: Optional[date] = Query(default=None),
    period_end: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    """Calculate driver trip-mileage pay and safety incentives."""
    end_dt = period_end or date.today()
    start_dt = period_start or (end_dt - timedelta(days=7))
    service = PayrollService(db)
    return service.calculate_fleet_payroll(period_start=start_dt, period_end=end_dt)
