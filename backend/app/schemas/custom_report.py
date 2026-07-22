from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

# Shared properties
class CustomReportBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    module: str
    selected_fields: List[str]
    filters: Optional[List[Dict[str, Any]]] = None
    group_by: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    chart_type: Optional[str] = None
    export_formats: Optional[List[str]] = None
    is_public: Optional[bool] = False

class CustomReportCreate(CustomReportBase):
    pass

class CustomReportUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    module: Optional[str] = None
    selected_fields: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    group_by: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None
    chart_type: Optional[str] = None
    export_formats: Optional[List[str]] = None
    is_public: Optional[bool] = None

class CustomReportResponse(CustomReportBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomReportListResponse(BaseModel):
    items: List[CustomReportResponse]
    total: int

class ExecuteReportRequest(BaseModel):
    filters_override: Optional[List[Dict[str, Any]]] = None

class ReportExecutionResponse(BaseModel):
    id: UUID
    report_id: UUID
    executed_by: Optional[UUID] = None
    execution_time: datetime
    duration_ms: int
    status: str
    row_count: int
    file_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ScheduleReportRequest(BaseModel):
    frequency: str  # 'daily', 'weekly', 'monthly', 'custom'
    cron_expression: Optional[str] = None
    email_recipients: Optional[List[str]] = None
    is_active: Optional[bool] = True

class ScheduleReportResponse(ScheduleReportRequest):
    id: UUID
    report_id: UUID
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatisticsResponse(BaseModel):
    total_reports: int
    public_reports: int
    my_reports: int
    total_executions: int
    avg_execution_time_ms: float
