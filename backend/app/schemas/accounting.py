"""
Fleet Accounting & Financial Ledger Pydantic Schemas.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
from pydantic import BaseModel, Field


class FinancialStatement(BaseModel):
    """Profit and Loss (P&L) Statement for fleet operations."""
    period_start: date
    period_end: date
    gross_freight_revenue: float
    fuel_expenses: float
    maintenance_expenses: float
    driver_payroll_expenses: float
    operational_tolls_expenses: float
    total_operating_expenses: float
    net_operating_profit: float
    operating_margin_percent: float


class LedgerEntry(BaseModel):
    """General Ledger Entry."""
    entry_id: UUID
    account_code: str  # e.g., "4000-REVENUE", "5000-FUEL", "5100-MAINTENANCE"
    account_name: str
    debit_usd: float
    credit_usd: float
    date: date
    description: str
