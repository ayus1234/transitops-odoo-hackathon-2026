"""
Unit & Integration tests for Extended Fleet Suite: AI Copilot, Payroll, CRM, Accounting, and Warehouse.
"""
import pytest
from datetime import date, timedelta
from app.schemas.ai_copilot import AICopilotQueryRequest
from app.services.ai_copilot_service import AICopilotService
from app.services.payroll_service import PayrollService
from app.services.crm_service import CRMService
from app.services.accounting_service import AccountingService
from app.services.warehouse_service import WarehouseService


def test_ai_copilot_natural_language_queries(db_session):
    copilot_service = AICopilotService(db_session)

    # 1. Health Query
    res_health = copilot_service.process_query(AICopilotQueryRequest(prompt="What is the overall fleet health condition?"))
    assert res_health.intent == "FLEET_HEALTH"
    assert "fleet health score" in res_health.answer.lower()

    # 2. Fuel Query
    res_fuel = copilot_service.process_query(AICopilotQueryRequest(prompt="Are there any fuel theft anomalies detected?"))
    assert res_fuel.intent == "FUEL_CHECK"

    # 3. Recommendation Query
    res_rec = copilot_service.process_query(AICopilotQueryRequest(prompt="Recommend the best vehicle to assign"))
    assert res_rec.intent == "RECOMMENDATION"


def test_fleet_payroll_calculations(db_session):
    payroll_service = PayrollService(db_session)
    end_dt = date.today()
    start_dt = end_dt - timedelta(days=7)

    summary = payroll_service.calculate_fleet_payroll(period_start=start_dt, period_end=end_dt)

    assert summary.total_drivers_paid >= 0
    assert summary.period_start == start_dt
    assert summary.period_end == end_dt


def test_logistics_crm_client_accounts(db_session):
    crm_service = CRMService(db_session)
    clients = crm_service.get_client_accounts()

    assert len(clients) >= 2
    apex = next(c for c in clients if "Apex" in c.company_name)
    assert apex.contract_tier == "Enterprise"
    assert apex.credit_limit_usd == 50000.0


def test_fleet_financial_accounting(db_session):
    accounting_service = AccountingService(db_session)
    end_dt = date.today()
    start_dt = end_dt - timedelta(days=30)

    pnl = accounting_service.generate_profit_loss_statement(period_start=start_dt, period_end=end_dt)

    assert pnl.gross_freight_revenue > 0.0
    assert pnl.total_operating_expenses > 0.0
    assert pnl.operating_margin_percent != 0.0


def test_yard_warehouse_loading_docks(db_session):
    warehouse_service = WarehouseService(db_session)
    staging = warehouse_service.get_yard_staging_summary()

    assert staging.total_loading_bays == 4
    assert staging.staged_pallets_count == 142
    assert len(staging.bays) == 4
