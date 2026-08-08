"""
Yard & Warehouse Loading Bay Management Service.
Manages warehouse loading dock bays, staged pallet inventory, and vehicle turnaround times.
"""
from typing import List
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.schemas.warehouse import LoadingBayStatus, WarehouseStagingSummary


class WarehouseService:
    """Service managing warehouse staging docks and yard loading bays."""

    def __init__(self, db: Session):
        self.db = db

    def get_yard_staging_summary(self) -> WarehouseStagingSummary:
        """Fetch current loading bay occupancy and staging inventory."""
        assigned_vehicles = self.db.query(Vehicle).filter(Vehicle.status == "Assigned").all()
        v_regs = [getattr(v, "registration_number", "TRK-101") for v in assigned_vehicles]

        bays = [
            LoadingBayStatus(
                bay_id="BAY-01",
                bay_name="Dock 1 - Dry Cargo Inbound",
                status="Occupied" if len(v_regs) > 0 else "Available",
                assigned_vehicle_registration=v_regs[0] if len(v_regs) > 0 else None,
                cargo_type="Dry Goods",
                estimated_turnaround_minutes=45
            ),
            LoadingBayStatus(
                bay_id="BAY-02",
                bay_name="Dock 2 - Cold Chain Outbound",
                status="Occupied" if len(v_regs) > 1 else "Available",
                assigned_vehicle_registration=v_regs[1] if len(v_regs) > 1 else None,
                cargo_type="Perishables",
                estimated_turnaround_minutes=30
            ),
            LoadingBayStatus(
                bay_id="BAY-03",
                bay_name="Dock 3 - Fast Track Express",
                status="Available",
                assigned_vehicle_registration=None,
                cargo_type="General Express",
                estimated_turnaround_minutes=20
            ),
            LoadingBayStatus(
                bay_id="BAY-04",
                bay_name="Dock 4 - Heavy Freight Bay",
                status="Available",
                assigned_vehicle_registration=None,
                cargo_type="Industrial Parts",
                estimated_turnaround_minutes=60
            )
        ]

        occupied = sum(1 for b in bays if b.status == "Occupied")

        return WarehouseStagingSummary(
            total_loading_bays=len(bays),
            occupied_bays=occupied,
            available_bays=len(bays) - occupied,
            staged_pallets_count=142,
            bays=bays
        )
