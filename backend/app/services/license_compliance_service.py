from typing import Dict, Any
from sqlalchemy.orm import Session
from app.repositories.license_compliance_repository import LicenseComplianceRepository
from app.services.activity_service import activity_service
from app.services.notification_service import NotificationService
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.schemas.activity import ActivityCreate
import csv
import io
import json
from app.utils.pdf_generator import generate_pdf_table

class LicenseComplianceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LicenseComplianceRepository(db)
        self.notification_service = NotificationService(db)

    def get_summary(self, user_id: str = None) -> Dict[str, Any]:
        return self.repo.get_summary(user_id)

    def get_paginated_compliance(self, skip: int = 0, limit: int = 10, search: str = None, status_filter: str = None, user_id: str = None, current_user: Any = None) -> Dict[str, Any]:
        data, total = self.repo.search_and_filter(skip, limit, search, status_filter, user_id)
        
        if current_user:
            activity_service.log_activity(
                self.db,
                ActivityCreate(
                    user_id=current_user.id,
                    module=ModuleEnum.DASHBOARD,
                    activity_type=ActivityTypeEnum.SYSTEM,
                    title="Viewed License Compliance",
                    description="User viewed the License Compliance dashboard.",
                    severity=SeverityEnum.INFO
                )
            )
            
            # Dynamic triggers for demo effect
            summary = self.get_summary(user_id)
            if summary["expired_licenses"] > 0:
                self.notification_service.notify_user(
                    db=self.db,
                    user_id=current_user.id,
                    title="Licence Expired",
                    description=f"{summary['expired_licenses']} license(s) have expired.",
                    type="Critical",
                    priority="High",
                    category="System",
                    module_name="Dashboard"
                )
            if summary["expiring_in_7_days"] > 0:
                self.notification_service.notify_user(
                    db=self.db,
                    user_id=current_user.id,
                    title="Licence Expiring Soon",
                    description=f"{summary['expiring_in_7_days']} license(s) expiring within 7 days.",
                    type="Warning",
                    priority="Medium",
                    category="System",
                    module_name="Dashboard"
                )
            
        return {
            "data": data,
            "pagination": {
                "total_items": total,
                "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
                "current_page": (skip // limit) + 1 if limit > 0 else 1,
                "page_size": limit
            },
            "success": True
        }

    def export_csv(self, user_id: str = None) -> str:
        data, _ = self.repo.search_and_filter(skip=0, limit=10000, user_id=user_id)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Full Name", "License Number", "Category", "Expiry Date", "Status"])
        for row in data:
            writer.writerow([
                str(row["id"]), row["full_name"], row["license_number"], 
                row["license_category"], row["license_expiry_date"], row["status"]
            ])
            
        return output.getvalue()
        
    def export_pdf(self, user_id: str = None) -> bytes:
        data, _ = self.repo.search_and_filter(skip=0, limit=10000, user_id=user_id)
        headers = ["Full Name", "License Number", "Category", "Expiry Date", "Status"]
        rows = [
            [row["full_name"], row["license_number"], row["license_category"], row["license_expiry_date"], row["status"]]
            for row in data
        ]
        return generate_pdf_table("License Compliance Report", headers, rows)
