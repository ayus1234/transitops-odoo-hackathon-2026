import os
import sys
import traceback
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.email.ilike('%admin%')).first()
    print("User:", user.email, user.password_hash)
except Exception as e:
    print(e)


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.core.database import SessionLocal
from app.services.license_compliance_service import LicenseComplianceService
from app.services.inventory_service import InventoryService
from app.services.report_service import ReportService

print("Testing Export CSV...")
db = SessionLocal()
try:
    svc = LicenseComplianceService(db)
    res = svc.export_pdf(None)
    print("PDF Export Successful, length:", len(res))
except Exception as e:
    print("CSV Export Failed!")
    traceback.print_exc()

print("\nTesting Inventory KPIs...")
try:
    inv = InventoryService(db)
    kpis = inv.get_dashboard_summary()
    print("KPIs:", kpis)
except Exception as e:
    print("Inventory KPIs Failed!")
    traceback.print_exc()

print("\nTesting Report Trips (dynamic data)...")
try:
    rep = ReportService(db)
    from datetime import date, timedelta
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    trips = rep.generate_trip_report(start_date=start_date, end_date=end_date)
    print("Trips dynamic data length (with dates):", len(trips))
except Exception as e:
    print("Trips Report Failed!")
    traceback.print_exc()
    
db.close()
