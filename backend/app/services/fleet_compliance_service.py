from typing import Dict, Any
from sqlalchemy.orm import Session
from app.repositories.fleet_compliance_repository import FleetComplianceRepository
from app.services.activity_service import activity_service
from app.services.notification_service import NotificationService
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.schemas.activity import ActivityCreate
import csv
import io
import json
from app.utils.pdf_generator import generate_pdf_table

class FleetComplianceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FleetComplianceRepository(db)
        self.notification_service = NotificationService(db)

    def get_summary(self, current_user: Any = None) -> Dict[str, float]:
        summary = self.repo.get_summary()
        
        if current_user:
            activity_service.log_activity(
                self.db,
                ActivityCreate(
                    user_id=current_user.id,
                    module=ModuleEnum.DASHBOARD,
                    activity_type=ActivityTypeEnum.SYSTEM,
                    title="Viewed Fleet Compliance",
                    description="User viewed the Fleet Compliance report.",
                    severity=SeverityEnum.INFO
                )
            )
            
            if summary.get("fleet_compliance_score", 100) < 70:
                self.notification_service.notify_user(
                    db=self.db,
                    user_id=current_user.id,
                    title="Low Fleet Compliance",
                    description=f"Fleet compliance is at {summary['fleet_compliance_score']}%. Please investigate.",
                    type="Critical",
                    priority="High",
                    category="System",
                    module_name="Dashboard"
                )
                
        return summary
        
    def get_analytics(self) -> Dict[str, Any]:
        return self.repo.get_analytics()

    def get_list(self) -> Dict[str, Any]:
        return self.repo.get_list()

    def export_csv(self) -> str:
        summary = self.repo.get_summary()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Score"])
        for key, value in summary.items():
            writer.writerow([key.replace('_', ' ').title(), value])
            
        return output.getvalue()
        
    def export_pdf(self) -> bytes:
        summary = self.repo.get_summary()
        headers = ["Metric", "Score"]
        rows = [[key.replace('_', ' ').title(), str(value)] for key, value in summary.items()]
        return generate_pdf_table("Fleet Compliance Report", headers, rows)
