from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date, timedelta
from app.models.driver import Driver
from app.models.user import User

class LicenseComplianceRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_status(self, expiry_date: date, driver_status: str) -> str:
        if driver_status == "Suspended":
            return "Suspended"
        
        today = date.today()
        if expiry_date < today:
            return "Expired"
        elif expiry_date <= today + timedelta(days=7):
            return "Expiring in 7 Days"
        elif expiry_date <= today + timedelta(days=30):
            return "Expiring Soon"
        return "Valid"

    def get_summary(self, user_id: str = None) -> Dict[str, Any]:
        query = self.db.query(Driver)
        if user_id:
            query = query.filter(Driver.user_id == user_id)
        
        drivers = query.all()
        total = len(drivers)
        
        today = date.today()
        in_7_days = today + timedelta(days=7)
        in_30_days = today + timedelta(days=30)
        
        valid = 0
        expired = 0
        expiring_7 = 0
        expiring_30 = 0
        
        for d in drivers:
            if d.license_expiry_date < today:
                expired += 1
            else:
                valid += 1
                if d.license_expiry_date <= in_7_days:
                    expiring_7 += 1
                elif d.license_expiry_date <= in_30_days:
                    expiring_30 += 1
        
        compliance_pct = round((valid / total * 100), 2) if total > 0 else 100.0
        
        return {
            "total_drivers": total,
            "valid_licenses": valid,
            "expired_licenses": expired,
            "expiring_in_7_days": expiring_7,
            "expiring_in_30_days": expiring_30,
            "compliance_percentage": compliance_pct
        }

    def search_and_filter(self, 
        skip: int = 0, 
        limit: int = 10, 
        search: str = None, 
        status_filter: str = None,
        user_id: str = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        
        query = self.db.query(Driver, User).join(User, Driver.user_id == User.id)
        
        if user_id:
            query = query.filter(Driver.user_id == user_id)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    Driver.license_number.ilike(search_term)
                )
            )
            
        all_results = query.all()
        
        # Process and filter in memory to easily handle dynamic statuses
        processed = []
        for driver, user in all_results:
            status = self._get_status(driver.license_expiry_date, driver.status)
            
            if status_filter:
                if status_filter == "Expiring Soon" and status not in ["Expiring Soon", "Expiring in 7 Days"]:
                    continue
                elif status_filter != "Expiring Soon" and status != status_filter:
                    if status_filter == "Valid" and status in ["Expiring Soon", "Expiring in 7 Days"]:
                        pass # These are technically still valid, but we might want them separate. Let's strictly match.
                    else:
                        continue
            
            processed.append({
                "id": driver.id,
                "full_name": user.full_name,
                "license_number": driver.license_number,
                "license_category": driver.license_category,
                "license_expiry_date": driver.license_expiry_date,
                "status": status,
                "days_remaining": (driver.license_expiry_date - date.today()).days
            })
            
        total = len(processed)
        paginated = processed[skip:skip+limit]
        
        return paginated, total
