"""
Yard & Warehouse Inventory Management Pydantic Schemas.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class LoadingBayStatus(BaseModel):
    """Warehouse loading dock bay status."""
    bay_id: str
    bay_name: str  # e.g., "Dock 1 - Inbound Cold Chain"
    status: str    # "Occupied", "Available", "Maintenance"
    assigned_vehicle_registration: Optional[str] = None
    cargo_type: str
    estimated_turnaround_minutes: int


class WarehouseStagingSummary(BaseModel):
    """Warehouse staging yard overview."""
    total_loading_bays: int
    occupied_bays: int
    available_bays: int
    staged_pallets_count: int
    bays: List[LoadingBayStatus]
