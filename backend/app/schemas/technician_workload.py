"""
Schemas for Technician Workload Management module.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime, time
from decimal import Decimal

# ---------------------------------------------------------
# TECHNICIAN SCHEMAS
# ---------------------------------------------------------

class TechnicianSummaryResponse(BaseModel):
    """Summary statistics for technicians."""
    total_technicians: int
    active_technicians: int
    available_technicians: int
    assigned_technicians: int
    overloaded_technicians: int
    technician_utilization_pct: float

class TechnicianDetail(BaseModel):
    """Detailed profile of a technician."""
    id: UUID
    name: str
    assigned_vehicles: int
    assigned_jobs: int
    current_workload: int
    utilization_pct: float
    status: str
    skills: List[str]
    experience_level: str
    
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# TASK SCHEMAS (using existing Maintenance fields)
# ---------------------------------------------------------

class TaskSummaryResponse(BaseModel):
    """Summary statistics for maintenance tasks."""
    total_tasks: int
    pending_tasks: int
    scheduled_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int

class TaskDetail(BaseModel):
    """Detailed representation of a maintenance task."""
    task_id: UUID
    vehicle_id: UUID
    vehicle_name: str
    vehicle_number: str
    maintenance_type: str
    assigned_technician: Optional[str]
    priority: str
    status: str
    scheduled_date: date
    estimated_duration: Optional[int]
    completion_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TaskAssignRequest(BaseModel):
    technician_name: str
