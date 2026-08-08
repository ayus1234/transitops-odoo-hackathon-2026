"""
Fleet Accounting API Router.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.core.database import get_db
from app.api.deps import PermissionChecker
from app.models.user import User
from app.schemas.accounting import FinancialStatement
from app.services.accounting_service import AccountingService

router = APIRouter(prefix="/accounting", tags=["Fleet Financial Accounting"])


@router.get("/profit-loss", response_model=FinancialStatement)
def get_profit_loss_statement(
    period_start: Optional[date] = Query(default=None),
    period_end: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    """Get Profit & Loss (P&L) financial statement."""
    end_dt = period_end or date.today()
    start_dt = period_start or (end_dt - timedelta(days=30))
    service = AccountingService(db)
    return service.generate_profit_loss_statement(period_start=start_dt, period_end=end_dt)
