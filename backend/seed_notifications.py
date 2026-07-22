import sys
import os
from uuid import uuid4
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User

def seed_notifications():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found. Please run main seeder first.")
            return
            
        modules = [
            {"name": "Vehicles", "routes": ["/vehicles", "/vehicles/status"], "icons": ["Truck", "Car"]},
            {"name": "Drivers", "routes": ["/drivers", "/drivers/compliance"], "icons": ["Users", "UserCheck"]},
            {"name": "Trips", "routes": ["/trips", "/trips/active"], "icons": ["Map", "Navigation"]},
            {"name": "Maintenance", "routes": ["/maintenance", "/maintenance/schedule"], "icons": ["Wrench", "Tool"]},
            {"name": "Fuel", "routes": ["/fuel", "/fuel/logs"], "icons": ["Fuel", "Battery"]},
            {"name": "Expenses", "routes": ["/expenses"], "icons": ["DollarSign", "CreditCard"]},
            {"name": "Reports", "routes": ["/reports"], "icons": ["FileText", "PieChart"]},
            {"name": "Settings", "routes": ["/settings"], "icons": ["Settings", "Sliders"]},
            {"name": "System", "routes": ["/"], "icons": ["Activity", "Server"]}
        ]
        
        types = ["Info", "Success", "Warning", "Critical"]
        priorities = ["Low", "Medium", "High", "Critical"]
        
        templates = [
            {"desc": "Routine check required for {}.", "title": "Maintenance Reminder"},
            {"desc": "Record in {} has been updated successfully.", "title": "Record Updated"},
            {"desc": "Urgent attention needed for {} module.", "title": "System Alert"},
            {"desc": "New entry added in {}.", "title": "New Record"},
            {"desc": "Usage in {} is approaching limit.", "title": "Threshold Warning"},
            {"desc": "Monthly report for {} is ready to view.", "title": "Report Generated"},
            {"desc": "Action required regarding recent {} update.", "title": "Action Required"}
        ]
        
        notifications = []
        
        for i in range(250):
            user = random.choice(users)
            mod = random.choice(modules)
            t = random.choice(templates)
            type_ = random.choice(types)
            
            severity = "Info"
            if type_ == "Warning": severity = "Warning"
            if type_ == "Critical": severity = "Critical"
            if type_ == "Success": severity = "Success"
            
            created = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 24))
            
            notif = Notification(
                id=uuid4(),
                user_id=user.id,
                title=t["title"],
                description=t["desc"].format(mod["name"]),
                type=type_,
                priority=random.choice(priorities),
                category=mod["name"],
                module_name=mod["name"],
                severity=severity,
                icon_name=random.choice(mod["icons"]),
                route=random.choice(mod["routes"]),
                is_read=random.choice([True, False, False]),
                is_archived=random.choice([True, False, False, False, False]),
                created_at=created,
                updated_at=created
            )
            notifications.append(notif)
            
        db.add_all(notifications)
        db.commit()
        print(f"Seeded {len(notifications)} notifications successfully!")
    except Exception as e:
        print(f"Error seeding notifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_notifications()
