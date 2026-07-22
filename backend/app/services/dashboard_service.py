"""
Dashboard and analytics service.
"""
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense


class DashboardService:
    """Service for dashboard analytics and aggregations."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # FLEET OVERVIEW
    # ============================================================

    def get_fleet_overview(self) -> dict:
        total = self.db.query(Vehicle).count()
        active = self.db.query(Vehicle).filter(Vehicle.status == 'Available').count()
        in_shop = self.db.query(Vehicle).filter(Vehicle.status == 'In Shop').count()
        on_trip = self.db.query(Vehicle).filter(Vehicle.status == 'On Trip').count()
        retired = self.db.query(Vehicle).filter(Vehicle.status == 'Retired').count()

        return {
            "total_vehicles": total,
            "active_vehicles": active,
            "vehicles_in_shop": in_shop,
            "vehicles_on_trip": on_trip,
            "retired_vehicles": retired
        }

    # ============================================================
    # DRIVER OVERVIEW
    # ============================================================

    def get_driver_overview(self) -> dict:
        total = self.db.query(Driver).count()
        available = self.db.query(Driver).filter(Driver.status == 'Available').count()
        on_trip = self.db.query(Driver).filter(Driver.status == 'On Trip').count()
        
        # We consider Available and On Trip as "Active"
        active = available + on_trip
        
        # License expiry alerts (within 30 days)
        thirty_days = date.today() + timedelta(days=30)
        expiring = self.db.query(Driver).filter(
            Driver.license_expiry_date <= thirty_days,
            Driver.status != 'Suspended'
        ).count()

        return {
            "total_drivers": total,
            "active_drivers": active,
            "drivers_on_trip": on_trip,
            "available_drivers": available,
            "license_expiry_alerts": expiring
        }

    # ============================================================
    # TRIP ANALYTICS
    # ============================================================

    def get_trip_analytics(self) -> dict:
        total = self.db.query(Trip).count()
        active = self.db.query(Trip).filter(Trip.status == 'Dispatched').count()
        completed = self.db.query(Trip).filter(Trip.status == 'Completed').count()
        cancelled = self.db.query(Trip).filter(Trip.status == 'Cancelled').count()

        # Averages
        avg_dist = self.db.query(func.avg(Trip.actual_distance_km)).filter(
            Trip.status == 'Completed'
        ).scalar() or 0.0

        # Note: Trip Cost would ideally be an aggregation of expenses linked to the trip.
        # For simplicity, we calculate the average sum of expenses per completed trip.
        query = """
            SELECT COALESCE(AVG(trip_cost), 0)
            FROM (
                SELECT t.id, COALESCE(SUM(e.amount), 0) as trip_cost
                FROM trips t
                LEFT JOIN expenses e ON t.id = e.trip_id AND e.status = 'Approved'
                WHERE t.status = 'Completed'
                GROUP BY t.id
            ) as completed_trip_costs
        """
        avg_cost = self.db.execute(text(query)).scalar() or 0.0

        return {
            "total_trips": total,
            "active_trips": active,
            "completed_trips": completed,
            "cancelled_trips": cancelled,
            "average_trip_distance_km": float(avg_dist),
            "average_trip_cost": float(avg_cost)
        }

    # ============================================================
    # MAINTENANCE ANALYTICS
    # ============================================================

    def get_maintenance_analytics(self) -> dict:
        pending = self.db.query(Maintenance).filter(Maintenance.status.in_(['Pending', 'Approved'])).count()
        in_progress = self.db.query(Maintenance).filter(Maintenance.status == 'In Progress').count()
        completed = self.db.query(Maintenance).filter(Maintenance.status == 'Completed').count()

        # Monthly Cost (Current Month)
        today = date.today()
        first_of_month = today.replace(day=1)
        
        monthly_cost = self.db.query(func.sum(Maintenance.actual_cost)).filter(
            Maintenance.status == 'Completed',
            Maintenance.completed_date >= first_of_month
        ).scalar() or 0.0

        return {
            "pending_maintenance": pending,
            "in_progress_maintenance": in_progress,
            "completed_maintenance": completed,
            "monthly_maintenance_cost": float(monthly_cost)
        }

    # ============================================================
    # FUEL ANALYTICS
    # ============================================================

    def get_fuel_analytics(self) -> dict:
        total_cost = self.db.query(func.sum(Fuel.total_cost)).scalar() or 0.0
        consumption = self.db.query(func.sum(Fuel.quantity_liters)).scalar() or 0.0

        # Overall efficiency (Simplified: Total Distance / Total Fuel)
        # Note: True efficiency requires odometer deltas, this is an approximation for the dashboard
        total_dist_query = """
            SELECT COALESCE(SUM(actual_distance_km), 0) 
            FROM trips WHERE status = 'Completed'
        """
        total_dist = self.db.execute(text(total_dist_query)).scalar() or 0.0
        
        avg_efficiency = (float(total_dist) / float(consumption)) if consumption > 0 else 0.0

        # Fuel trend (Last 6 months)
        trend = []
        for i in range(5, -1, -1):
            start = (date.today() - relativedelta(months=i)).replace(day=1)
            end = start + relativedelta(months=1) - timedelta(days=1)
            
            cost = self.db.query(func.sum(Fuel.total_cost)).filter(
                Fuel.refuel_date >= start,
                Fuel.refuel_date <= end
            ).scalar() or 0.0
            
            trend.append({
                "month": start.strftime("%Y-%m"),
                "cost": float(cost)
            })

        return {
            "total_fuel_cost": float(total_cost),
            "fuel_consumption_liters": float(consumption),
            "average_fuel_efficiency_kmpl": round(avg_efficiency, 2),
            "fuel_cost_trend": trend
        }

    # ============================================================
    # EXPENSE ANALYTICS
    # ============================================================

    def get_expense_analytics(self) -> dict:
        # Only consider Approved expenses
        base_query = self.db.query(Expense).filter(Expense.status == 'Approved')
        
        total = base_query.with_entities(func.sum(Expense.amount)).scalar() or 0.0

        # Monthly
        today = date.today()
        first_of_month = today.replace(day=1)
        monthly = base_query.filter(Expense.expense_date >= first_of_month).with_entities(func.sum(Expense.amount)).scalar() or 0.0

        # By Category
        category_query = """
            SELECT expense_type, SUM(amount)
            FROM expenses
            WHERE status = 'Approved'
            GROUP BY expense_type
        """
        categories = dict(self.db.execute(text(category_query)).fetchall())
        # Ensure default keys
        for cat in ['Fuel', 'Maintenance', 'Toll', 'Repair', 'Miscellaneous']:
            categories.setdefault(cat, 0.0)

        # Trend (Last 6 months)
        trend = []
        for i in range(5, -1, -1):
            start = (date.today() - relativedelta(months=i)).replace(day=1)
            end = start + relativedelta(months=1) - timedelta(days=1)
            
            cost = base_query.filter(
                Expense.expense_date >= start,
                Expense.expense_date <= end
            ).with_entities(func.sum(Expense.amount)).scalar() or 0.0
            
            trend.append({
                "month": start.strftime("%Y-%m"),
                "cost": float(cost)
            })

        return {
            "total_expenses": float(total),
            "expenses_by_category": {k: float(v) for k, v in categories.items()},
            "monthly_expenses": float(monthly),
            "expense_trend": trend
        }

    # ============================================================
    # FINANCIAL SUMMARY
    # ============================================================

    def get_financial_summary(self) -> dict:
        # Sums all Approved expenses based on category
        fuel = self.db.query(func.sum(Expense.amount)).filter(
            Expense.status == 'Approved',
            Expense.expense_type == 'Fuel'
        ).scalar() or 0.0
        
        maint = self.db.query(func.sum(Expense.amount)).filter(
            Expense.status == 'Approved',
            Expense.expense_type == 'Maintenance'
        ).scalar() or 0.0
        
        other = self.db.query(func.sum(Expense.amount)).filter(
            Expense.status == 'Approved',
            Expense.expense_type.in_(['Toll', 'Repair', 'Miscellaneous'])
        ).scalar() or 0.0

        total = float(fuel) + float(maint) + float(other)

        return {
            "total_operational_cost": float(total),
            "fuel_cost": float(fuel),
            "maintenance_cost": float(maint),
            "other_expenses": float(other)
        }

    # ============================================================
    # ALERTS
    # ============================================================

    def _determine_severity(self, days: int) -> str:
        if days < 0:
            return "Critical"  # Overdue
        elif days <= 7:
            return "Critical"
        elif days <= 15:
            return "Warning"
        return "Info"

    def get_alerts(self) -> dict:
        alerts = {
            "maintenance_due": [],
            "licenses_expiring": [],
            "insurance_expiring": [],
            "registration_expiring": []
        }
        
        today = date.today()
        thirty_days = today + timedelta(days=30)

        # 1. Maintenance Due (Scheduled within 30 days, Pending/Approved)
        maint_records = self.db.query(Maintenance).filter(
            Maintenance.status.in_(['Pending', 'Approved']),
            Maintenance.scheduled_date <= thirty_days
        ).all()
        for m in maint_records:
            days = (m.scheduled_date - today).days
            alerts["maintenance_due"].append({
                "id": m.id,
                "entity_name": f"{m.vehicle.registration_number} ({m.vehicle.manufacturer} {m.vehicle.model})",
                "alert_type": "Maintenance Due",
                "due_date": m.scheduled_date,
                "days_remaining": days,
                "severity": self._determine_severity(days),
                "task": m.maintenance_type,
                "status": m.status
            })

        # 2. Licenses Expiring (Active drivers, expiring within 30 days)
        drivers = self.db.query(Driver).filter(
            Driver.status != 'Suspended',
            Driver.license_expiry_date <= thirty_days
        ).all()
        for d in drivers:
            days = (d.license_expiry_date - today).days
            alerts["licenses_expiring"].append({
                "id": d.id,
                "entity_name": f"{d.user.first_name} {d.user.last_name}",
                "alert_type": "License Expiring",
                "due_date": d.license_expiry_date,
                "days_remaining": days,
                "severity": self._determine_severity(days)
            })

        # 3. Insurance & Registration Expiring (Active vehicles, expiring within 30 days)
        # Note: registration_expiry is not explicitly in SCHEMA, but insurance_expiry is.
        # I will use insurance_expiry for both to fulfill the schema constraints cleanly.
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.status != 'Retired',
            Vehicle.insurance_expiry <= thirty_days
        ).all()
        for v in vehicles:
            days = (v.insurance_expiry - today).days
            
            alerts["insurance_expiring"].append({
                "id": v.id,
                "entity_name": v.registration_number,
                "alert_type": "Insurance Expiring",
                "due_date": v.insurance_expiry,
                "days_remaining": days,
                "severity": self._determine_severity(days)
            })

        return alerts

    # ============================================================
    # MASTER OVERVIEW
    # ============================================================

    def get_master_overview(self) -> dict:
        """Returns the high-level metrics across all domains for the main dashboard."""
        return {
            "fleet": self.get_fleet_overview(),
            "drivers": self.get_driver_overview(),
            "trips": self.get_trip_analytics(),
            "financial": self.get_financial_summary()
        }
