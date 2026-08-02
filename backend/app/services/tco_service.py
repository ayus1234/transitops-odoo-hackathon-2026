"""
Total Cost of Ownership (TCO) service layer for fleet cost aggregation.
"""
from typing import Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vehicle import Vehicle
from app.models.fuel import Fuel
from app.models.maintenance import Maintenance
from app.models.expense import Expense
from app.repositories.vehicle_repository import VehicleRepository
from app.utils.exceptions import NotFoundError


class TCOService:
    """Service for calculating Total Cost of Ownership (TCO) per vehicle."""

    def __init__(self, db: Session):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)

    def calculate_vehicle_tco(self, vehicle_id: UUID) -> dict:
        """
        Calculate full Total Cost of Ownership (TCO) breakdown for a vehicle.

        Aggregates:
        - Acquisition / Lease capital costs
        - Fuel expenditure (total fuel logs cost)
        - Maintenance & repairs expenditure (total maintenance logs cost)
        - Operational expenses (other linked expenses)
        - Cost per kilometer (total operational cost / odometer)

        Raises:
            NotFoundError: If vehicle not found
        """
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle with ID {vehicle_id} not found")

        # 1. Total Fuel Cost
        fuel_result = self.db.query(
            func.coalesce(func.sum(Fuel.total_cost), 0.0).label('total_fuel')
        ).filter(Fuel.vehicle_id == vehicle_id).first()
        total_fuel_cost = Decimal(str(fuel_result.total_fuel if fuel_result is not None else 0.0))

        # 2. Total Maintenance Cost
        maint_result = self.db.query(
            func.coalesce(func.sum(Maintenance.actual_cost), 0.0).label('total_maint')
        ).filter(
            Maintenance.vehicle_id == vehicle_id,
            Maintenance.status == 'Completed'
        ).first()
        total_maint_cost = Decimal(str(maint_result.total_maint if maint_result is not None else 0.0))

        # 3. Total Operational Expenses (linked to vehicle, non-fuel/non-maintenance to prevent double counting)
        expense_result = self.db.query(
            func.coalesce(func.sum(Expense.amount), 0.0).label('total_expenses')
        ).filter(
            Expense.vehicle_id == vehicle_id,
            Expense.status == 'Approved'
        ).first()
        total_expenses_cost = Decimal(str(expense_result.total_expenses if expense_result is not None else 0.0))

        # Capital Cost (Acquisition or Lease)
        acquisition_cost = Decimal(str(vehicle.acquisition_cost or 0.0))
        monthly_lease_cost = Decimal(str(vehicle.monthly_lease_cost or 0.0))

        # Total Operating Cost (Fuel + Maintenance + Expenses)
        total_operating_cost = total_fuel_cost + total_maint_cost + total_expenses_cost

        # Total Lifetime Cost (Operating + Capital)
        total_tco = total_operating_cost + acquisition_cost

        # Metrics per km
        odometer_km = Decimal(str(vehicle.current_odometer_km or 0.0))
        cost_per_km = (total_operating_cost / odometer_km) if odometer_km > 0 else None
        fuel_cost_per_km = (total_fuel_cost / odometer_km) if odometer_km > 0 else None
        maint_cost_per_km = (total_maint_cost / odometer_km) if odometer_km > 0 else None

        return {
            "vehicle_id": str(vehicle_id),
            "registration_number": vehicle.registration_number,
            "vehicle_name": vehicle.vehicle_name,
            "current_odometer_km": float(odometer_km),
            "cost_breakdown": {
                "acquisition_cost": float(acquisition_cost),
                "monthly_lease_cost": float(monthly_lease_cost),
                "total_fuel_cost": float(total_fuel_cost),
                "total_maintenance_cost": float(total_maint_cost),
                "total_other_expenses": float(total_expenses_cost),
                "total_operating_cost": float(total_operating_cost),
                "total_tco": float(total_tco)
            },
            "unit_metrics": {
                "cost_per_km": float(cost_per_km) if cost_per_km is not None else None,
                "fuel_cost_per_km": float(fuel_cost_per_km) if fuel_cost_per_km is not None else None,
                "maintenance_cost_per_km": float(maint_cost_per_km) if maint_cost_per_km is not None else None
            }
        }
