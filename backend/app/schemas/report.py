"""
Schemas for report generation and responses.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import date
from uuid import UUID

# ============================================================
# Query Parameters Schema
# ============================================================

class ReportParams(BaseModel):
    """Common parameters for report generation."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    status: Optional[str] = None
    export_format: str = "json"  # json, csv, xlsx, pdf


# ============================================================
# Standard JSON Response Wrapper
# ============================================================

class ReportResponse(BaseModel):
    """Standard JSON response for reports."""
    success: bool = True
    report_type: str
    metadata: Dict[str, Any]
    data: List[Dict[str, Any]]
