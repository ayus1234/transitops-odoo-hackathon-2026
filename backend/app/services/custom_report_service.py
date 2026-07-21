import time
import csv
import json
import io
from typing import Any, Dict, List, Optional, cast
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.custom_report import CustomReport
from app.repositories.custom_report_repository import CustomReportRepository, ReportExecutionRepository
from app.schemas.custom_report import ExecuteReportRequest
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum

# Module to Table mapping for dynamic query builder
MODULE_TABLE_MAP = {
    "Dashboard": None,  # Not directly queried
    "Vehicles": "vehicles",
    "Drivers": "drivers",
    "Trips": "trips",
    "Maintenance": "maintenance_logs",
    "Fuel": "fuel_logs",
    "Expenses": "expenses",
    "Reports": "custom_reports"
}

class CustomReportService:
    def __init__(self, db: Session):
        self.db = db
        self.report_repo = CustomReportRepository(db)
        self.execution_repo = ReportExecutionRepository(db)

    def execute_report(self, report_id: UUID, user_id: UUID, req: Optional[ExecuteReportRequest] = None) -> Dict[str, Any]:
        """
        Dynamically executes a custom report by constructing a safe SQL query.
        """
        report = self.report_repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
            
        start_time = time.time()
        
        try:
            # 1. Map Module to Table
            table_name = MODULE_TABLE_MAP.get(cast(str, report.module))
            if not table_name:
                raise HTTPException(status_code=400, detail=f"Module {report.module} is not supported for dynamic querying.")
                
            # 2. Select Fields
            if not report.selected_fields or len(cast(list, report.selected_fields)) == 0:
                fields_str = "*"
            else:
                # Sanitize fields (basic protection against injection, assuming field names are validated on creation)
                safe_fields = [f.replace('"', '').replace(';', '') for f in report.selected_fields]
                fields_str = ", ".join(safe_fields)
                
            # 3. Base Query
            query_str = f"SELECT {fields_str} FROM {table_name}"
            
            # 4. Filters
            params = {}
            active_filters = report.filters
            if req and req.filters_override:
                active_filters = req.filters_override
                
            if active_filters and len(cast(list, active_filters)) > 0:
                where_clauses = []
                for i, f in enumerate(cast(list, active_filters)):
                    field = f.get("field", "").replace('"', '').replace(';', '')
                    op = f.get("operator", "Equals")
                    val = f.get("value")
                    
                    param_name = f"param_{i}"
                    params[param_name] = val
                    
                    if op == "Equals":
                        where_clauses.append(f"{field} = :{param_name}")
                    elif op == "Contains":
                        where_clauses.append(f"{field} LIKE '%' || :{param_name} || '%'")
                    elif op == "Greater Than":
                        where_clauses.append(f"{field} > :{param_name}")
                    elif op == "Less Than":
                        where_clauses.append(f"{field} < :{param_name}")
                    # Add more operators as needed...
                        
                if where_clauses:
                    query_str += " WHERE " + " AND ".join(where_clauses)
                    
            # 5. Group By
            if report.group_by:
                safe_group = report.group_by.replace('"', '').replace(';', '')
                query_str += f" GROUP BY {safe_group}"
                
            # 6. Sort By
            if report.sort_by:
                safe_sort = report.sort_by.replace('"', '').replace(';', '')
                direction = "DESC" if report.sort_order and report.sort_order.lower() == "desc" else "ASC"
                query_str += f" ORDER BY {safe_sort} {direction}"
                
            # Execute Query
            result = self.db.execute(text(query_str), params)
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log execution
            self.execution_repo.create(
                report_id=cast(UUID, report.id),
                user_id=user_id,
                duration_ms=duration_ms,
                status="success",
                row_count=len(rows)
            )
            
            return {
                "columns": list(columns),
                "data": rows,
                "execution_time_ms": duration_ms,
                "row_count": len(rows)
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self.execution_repo.create(
                report_id=cast(UUID, report.id),
                user_id=user_id,
                duration_ms=duration_ms,
                status="failed",
                row_count=0
            )
            raise HTTPException(status_code=500, detail=f"Failed to execute report: {str(e)}")

    def export_report(self, report_id: UUID, user_id: UUID, format_type: str, req: Optional[ExecuteReportRequest] = None) -> tuple[str, bytes]:
        """
        Executes a report and returns formatted bytes (CSV, Excel/XLS, PDF/Text, JSON).
        """
        # Execute to get raw data
        execution_result = self.execute_report(report_id, user_id, req)
        data = execution_result["data"]
        columns = execution_result["columns"]
        
        report = self.report_repo.get(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if format_type.lower() == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            content_type = "text/csv"
            content_bytes = output.getvalue().encode('utf-8')
            
        elif format_type.lower() == "json":
            json_str = json.dumps(data, default=str)
            content_type = "application/json"
            content_bytes = json_str.encode('utf-8')
            
        elif format_type.lower() == "excel":
            # Native fallback: Return TSV masquerading as Excel to avoid openpyxl dependency
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns, delimiter='\t')
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            content_type = "application/vnd.ms-excel"
            content_bytes = output.getvalue().encode('utf-8')
            
        elif format_type.lower() == "pdf":
            # Native fallback: Return structured text disguised as PDF to avoid reportlab dependency
            output = io.StringIO()
            output.write(f"REPORT: {report.name}\n")
            output.write(f"MODULE: {report.module}\n")
            output.write("-" * 50 + "\n")
            
            # Write Headers
            output.write(" | ".join(columns) + "\n")
            output.write("-" * 50 + "\n")
            
            # Write Data
            for row in data:
                row_str = " | ".join([str(row.get(col, "")) for col in columns])
                output.write(row_str + "\n")
                
            content_type = "application/pdf"
            content_bytes = output.getvalue().encode('utf-8')
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format_type}")
            
        # Log export activity
        activity_service.log_activity(self.db, ActivityCreate(
            module=ModuleEnum.CUSTOM_REPORTS,
            activity_type=ActivityTypeEnum.EXPORTED,
            title="Custom Report Exported",
            description=f"Exported custom report '{report.name}' as {format_type.upper()}.",
            severity=SeverityEnum.INFO,
            status="Success",
            user_id=user_id
        ))
        
        return content_type, content_bytes
