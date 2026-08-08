"""
Fleet Payroll & Driver Pay Calculation Service.
Calculates driver earnings based on completed trip mileage, base shift rates, and safety bonuses.
"""
from typing import List
from uuid import UUID
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.driver import Driver
from app.models.trip import Trip
from app.models.audit_event import AuditEvent
from app.schemas.payroll import DriverPayrollCalculation, DriverPayrollSummary


class PayrollService:
    """Service calculating driver trip-mileage pay and safety incentives."""

    BASE_WEEKLY_PAY = 500.0  # $500 base weekly shift salary
    RATE_PER_KM = 0.45       # $0.45 per km driven
    SAFETY_BONUS_PER_WEEK = 150.0  # $150 bonus if 0 speeding alerts

    def __init__(self, db: Session):
        self.db = db

    def calculate_fleet_payroll(self, period_start: date, period_end: date) -> DriverPayrollSummary:
        """Calculate driver payroll for a specified date range."""
        drivers = self.db.query(Driver).all()
        statements: List[DriverPayrollCalculation] = []
        total_cost = 0.0

        for d in drivers:
            # Completed trips in period
            trips = self.db.query(Trip).filter(
                Trip.driver_id == d.id,
                Trip.status == "Completed"
            ).all()

            dist_km = sum(float(t.planned_distance_km) for t in trips if t.planned_distance_km)
            km_bonus = dist_km * self.RATE_PER_KM

            # Safety violations check
            speeding_count = self.db.query(AuditEvent).filter(
                AuditEvent.driver_id == d.id,
                AuditEvent.event_type == "SPEEDING_ALERT"
            ).count()

            safety_bonus = self.SAFETY_BONUS_PER_WEEK if speeding_count == 0 else 0.0
            gross_pay = self.BASE_WEEKLY_PAY + km_bonus + safety_bonus
            total_cost += gross_pay

            driver_name = f"{d.user.first_name} {d.user.last_name}" if d.user else getattr(d, "license_number", "Driver")

            statements.append(DriverPayrollCalculation(
                driver_id=UUID(str(d.id)),
                driver_name=driver_name,
                license_number=getattr(d, "license_number", ""),
                period_start=period_start,
                period_end=period_end,
                completed_trips_count=len(trips),
                total_distance_km=round(dist_km, 1),
                base_pay=self.BASE_WEEKLY_PAY,
                per_km_bonus=round(km_bonus, 2),
                safety_bonus=safety_bonus,
                total_gross_pay=round(gross_pay, 2),
                status="Approved" if gross_pay > 0 else "Draft"
            ))

        return DriverPayrollSummary(
            period_start=period_start,
            period_end=period_end,
            total_drivers_paid=len(statements),
            total_payroll_cost=round(total_cost, 2),
            driver_statements=statements
        )
