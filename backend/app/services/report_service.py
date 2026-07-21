"""
Report service for generating data and formats.
"""
import csv
import io
from fpdf import FPDF
from datetime import date
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.utils.exceptions import BusinessLogicError
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User


class ReportService:
    """Service for generating comprehensive reports and handling exports."""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # DATA GENERATION
    # ============================================================

    def generate_fleet_report(self, status: str | None = None) -> List[Dict[str, Any]]:
        query = self.db.query(Vehicle)
        if status:
            query = query.filter(Vehicle.status == status)
            
        vehicles = query.all()
        return [{
            "Registration": v.registration_number,
            "Name": v.vehicle_name,
            "Type": v.vehicle_type,
            "Capacity (kg)": float(v.capacity_kg),
            "Odometer": float(v.current_odometer_km) if v.current_odometer_km else 0.0,
            "Status": v.status
        } for v in vehicles]

    def generate_driver_report(self, status: str | None = None) -> List[Dict[str, Any]]:
        query = self.db.query(Driver)
        if status:
            query = query.filter(Driver.status == status)
            
        drivers = query.all()
        return [{
            "Name": f"{d.user.first_name} {d.user.last_name}",
            "License": d.license_number,
            "Type": d.license_category,
            "Expiry": str(d.license_expiry_date),
            "Safety Score": float(d.safety_score),
            "Trips": d.total_trips,
            "Status": d.status
        } for d in drivers]

    def generate_trip_report(
        self, 
        start_date: date | None = None, 
        end_date: date | None = None,
        status: str | None = None
    ) -> List[Dict[str, Any]]:
        query = self.db.query(Trip)
        if status:
            query = query.filter(Trip.status == status)
        if start_date:
            query = query.filter(Trip.planned_departure >= start_date)
        if end_date:
            query = query.filter(Trip.planned_departure <= end_date)
            
        trips = query.all()
        return [{
            "Trip #": t.trip_number,
            "Vehicle": t.vehicle.registration_number,
            "Driver": f"{t.driver.user.first_name} {t.driver.user.last_name}",
            "Source": t.source,
            "Destination": t.destination,
            "Distance (km)": float(t.actual_distance_km) if t.actual_distance_km else 0.0,
            "Status": t.status
        } for t in trips]

    def generate_maintenance_report(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None
    ) -> List[Dict[str, Any]]:
        query = self.db.query(Maintenance)
        if status:
            query = query.filter(Maintenance.status == status)
        if start_date:
            query = query.filter(Maintenance.scheduled_date >= start_date)
        if end_date:
            query = query.filter(Maintenance.scheduled_date <= end_date)
            
        maint = query.all()
        return [{
            "Maint #": m.maintenance_number,
            "Vehicle": m.vehicle.registration_number,
            "Type": m.maintenance_type,
            "Priority": m.priority,
            "Cost": float(m.actual_cost) if m.actual_cost else 0.0,
            "Status": m.status
        } for m in maint]

    def generate_fuel_report(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> List[Dict[str, Any]]:
        query = self.db.query(Fuel)
        if start_date:
            query = query.filter(Fuel.refuel_date >= start_date)
        if end_date:
            query = query.filter(Fuel.refuel_date <= end_date)
            
        fuels = query.all()
        return [{
            "Vehicle": f.vehicle.registration_number,
            "Type": f.fuel_type,
            "Liters": float(f.quantity_liters),
            "Cost": float(f.total_cost),
            "Date": str(f.refuel_date.date())
        } for f in fuels]

    def generate_expense_report(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None
    ) -> List[Dict[str, Any]]:
        query = self.db.query(Expense)
        if status:
            query = query.filter(Expense.status == status)
        if start_date:
            query = query.filter(Expense.expense_date >= start_date)
        if end_date:
            query = query.filter(Expense.expense_date <= end_date)
            
        expenses = query.all()
        return [{
            "Type": e.expense_type,
            "Amount": float(e.amount),
            "Date": str(e.expense_date),
            "Vendor": e.vendor_name or "N/A",
            "Status": e.status
        } for e in expenses]

    # ============================================================
    # AGGREGATED REPORTS (Reusing Dashboard logic principles)
    # ============================================================

    def generate_financial_summary(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> List[Dict[str, Any]]:
        # Helper to apply date filters to queries
        def filter_by_date(q, date_column):
            if start_date:
                q = q.filter(date_column >= start_date)
            if end_date:
                q = q.filter(date_column <= end_date)
            return q

        # Aggregate Fuel Costs
        fuel_logs_q = self.db.query(func.sum(Fuel.total_cost))
        fuel_logs_q = filter_by_date(fuel_logs_q, Fuel.refuel_date)
        fuel_logs_cost = float(fuel_logs_q.scalar() or 0.0)

        fuel_expense_q = self.db.query(func.sum(Expense.amount)).filter(Expense.expense_type == 'Fuel', Expense.status == 'Approved')
        fuel_expense_q = filter_by_date(fuel_expense_q, Expense.expense_date)
        fuel_expense_cost = float(fuel_expense_q.scalar() or 0.0)
        
        fuel_cost = fuel_logs_cost + fuel_expense_cost

        # Aggregate Maintenance Costs
        maint_logs_q = self.db.query(func.sum(Maintenance.actual_cost)).filter(Maintenance.status == 'Completed')
        maint_logs_q = filter_by_date(maint_logs_q, Maintenance.scheduled_date)
        maint_logs_cost = float(maint_logs_q.scalar() or 0.0)

        maint_expense_q = self.db.query(func.sum(Expense.amount)).filter(Expense.expense_type == 'Maintenance', Expense.status == 'Approved')
        maint_expense_q = filter_by_date(maint_expense_q, Expense.expense_date)
        maint_expense_cost = float(maint_expense_q.scalar() or 0.0)
        
        maint_cost = maint_logs_cost + maint_expense_cost

        # Aggregate Other Operations Costs
        other_q = self.db.query(func.sum(Expense.amount)).filter(Expense.expense_type.not_in(['Fuel', 'Maintenance']), Expense.status == 'Approved')
        other_q = filter_by_date(other_q, Expense.expense_date)
        other_cost = float(other_q.scalar() or 0.0)
        
        return [
            {"Category": "Fuel", "Total Cost": float(fuel_cost)},
            {"Category": "Maintenance", "Total Cost": float(maint_cost)},
            {"Category": "Other Operations", "Total Cost": float(other_cost)},
            {"Category": "GRAND TOTAL", "Total Cost": float(fuel_cost + maint_cost + other_cost)}
        ]

    # ============================================================
    # EXPORT FORMATTERS
    # ============================================================

    def export_data(self, data: List[Dict[str, Any]], format_type: str, title: str, current_user: User = None) -> Tuple[Any, str, str]:
        """
        Export data to the requested format in memory.
        Returns (buffer/content, media_type, filename)
        """
        if not data:
            raise BusinessLogicError("No data available to export.")

        if format_type == "csv":
            return self._export_csv(data, title)
        elif format_type == "xlsx":
            return self._export_xlsx_fallback(data, title)
        elif format_type == "pdf":
            return self._export_pdf_fallback(data, title)
        else:
            raise BusinessLogicError(f"Unsupported export format: {format_type}")
            
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.REPORTS,
                activity_type=ActivityTypeEnum.EXPORTED,
                title="Report Exported",
                description=f"Exported {title} as {format_type.upper()}.",
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id
            ))
            
        return output, media_type, filename

    def _export_csv(self, data: List[Dict[str, Any]], title: str) -> Tuple[io.BytesIO, str, str]:
        string_output = io.StringIO()
        writer = csv.DictWriter(string_output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        
        # Convert to bytes for StreamingResponse
        byte_output = io.BytesIO(string_output.getvalue().encode('utf-8-sig'))
        byte_output.seek(0)
        return byte_output, "text/csv; charset=utf-8", f"{title.lower().replace(' ', '_')}.csv"

    def _export_xlsx_fallback(self, data: List[Dict[str, Any]], title: str) -> Tuple[io.BytesIO, str, str]:
        # Fallback to CSV format but with .xlsx extension/mimetype so Excel opens it
        output, _, filename = self._export_csv(data, title)
        return output, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename.replace('.csv', '.xlsx')

    def _export_pdf_fallback(self, data: List[Dict[str, Any]], title: str) -> Tuple[io.BytesIO, str, str]:
        """Generate a real binary PDF report using fpdf2."""
        headers = list(data[0].keys())
        generated_date = date.today().strftime("%B %d, %Y")

        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # --- Header ---
        pdf.set_fill_color(0, 64, 161)  # Primary blue
        pdf.rect(0, 0, 297, 38, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 18)
        pdf.set_xy(10, 8)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_x(10)
        pdf.cell(0, 5, f'TransitOps ERP  |  Generated: {generated_date}  |  Records: {len(data)}', ln=True)

        pdf.ln(10)

        # --- Table ---
        num_cols = len(headers)
        available_width = 277  # A4 landscape minus margins
        col_width = available_width / num_cols

        # Table header
        pdf.set_fill_color(241, 243, 245)
        pdf.set_text_color(73, 83, 87)
        pdf.set_font('Helvetica', 'B', 8)
        for h in headers:
            pdf.cell(col_width, 8, str(h)[:20], border=1, fill=True)
        pdf.ln()

        # Table rows
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(26, 28, 30)
        for i, row in enumerate(data):
            # Alternate row background
            if i % 2 == 0:
                pdf.set_fill_color(255, 255, 255)
            else:
                pdf.set_fill_color(248, 249, 250)

            for k in headers:
                val = row.get(k, '')
                if isinstance(val, float):
                    val = f'${val:,.2f}' if 'cost' in k.lower() or 'amount' in k.lower() else f'{val:,.2f}'
                pdf.cell(col_width, 7, str(val)[:30], border=1, fill=True)
            pdf.ln()

        # --- Footer ---
        pdf.ln(5)
        pdf.set_font('Helvetica', 'I', 7)
        pdf.set_text_color(134, 142, 150)
        pdf.cell(0, 5, '(C) 2026 TransitOps ERP. This report was auto-generated.', align='C')

        byte_output = io.BytesIO(pdf.output())
        byte_output.seek(0)
        return byte_output, "application/pdf", f"{title.lower().replace(' ', '_')}_report.pdf"

