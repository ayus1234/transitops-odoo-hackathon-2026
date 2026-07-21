import os
import sys
import random
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.role import Role
from app.models.help_center import SupportTicket
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.services.help_service import HelpService


def seed_support_tickets():
    print("Seeding Support Tickets...")
    
    # Schema changes are managed by Alembic in PostgreSQL
    # print("Recreating SupportTicket table for SQLite compatibility...")
    # SupportTicket.__table__.drop(engine, checkfirst=True)
    # SupportTicket.__table__.create(engine, checkfirst=True)
    
    db = SessionLocal()
    
    try:
        # Get users
        admin_role = db.query(Role).filter(Role.name == "System Admin").first()
        support_role = db.query(Role).filter(Role.name == "Support Agent").first()
        driver_role = db.query(Role).filter(Role.name == "Driver").first()
        fleet_manager_role = db.query(Role).filter(Role.name == "Fleet Manager").first()
        
        admins = db.query(User).filter(User.role_id == admin_role.id).all() if admin_role else []
        support_agents = db.query(User).filter(User.role_id == support_role.id).all() if support_role else []
        drivers = db.query(User).filter(User.role_id == driver_role.id).all() if driver_role else []
        fleet_managers = db.query(User).filter(User.role_id == fleet_manager_role.id).all() if fleet_manager_role else []
        
        creators = drivers + fleet_managers + admins
        assignees = admins + support_agents
        
        if not creators:
            print("Error: No valid users found to create tickets.")
            return
            
        if not assignees:
            assignees = creators

        modules = ["Vehicles", "Drivers", "Trips", "Maintenance", "Fuel", "Expenses", "Reports", "Settings", "Help Center", "Dashboard"]
        categories = ["Bug Report", "Feature Request", "Account Issue", "Billing", "General Inquiry"]
        priorities = ["Low", "Medium", "High", "Critical"]
        statuses = ["Open", "In Progress", "Resolved", "Closed"]

        service = HelpService(db)

        for i in range(50):
            creator = random.choice(creators)
            priority = random.choices(priorities, weights=[40, 30, 20, 10])[0]
            status = random.choices(statuses, weights=[30, 30, 20, 20])[0]
            
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            ticket_data = {
                "title": f"Issue with {random.choice(modules)} module ({i})",
                "description": f"Encountered an unexpected issue while using the platform. Please investigate ticket {i}.",
                "module_name": random.choice(modules),
                "category": random.choice(categories),
                "priority": priority,
                "status": status,
                "created_by": creator.id,
                "ticket_number": service.repository.generate_ticket_number(),
                "created_at": created_at,
                "updated_at": created_at
            }
            
            if status in ["In Progress", "Resolved", "Closed"]:
                ticket_data["assigned_to"] = random.choice(assignees).id
                
            if status in ["Resolved", "Closed"]:
                ticket_data["resolution_notes"] = f"Resolved issue successfully after investigation. Action taken for ticket {i}."
                ticket_data["resolved_at"] = created_at + timedelta(days=random.randint(1, 3))
                
            if status == "Closed":
                ticket_data["closed_at"] = ticket_data["resolved_at"] + timedelta(days=random.randint(1, 2))
                
            ticket = SupportTicket(**ticket_data)
            db.add(ticket)
            db.flush()
            
            activity_service.log_activity(db, ActivityCreate(
                module=ModuleEnum.HELP_CENTER,
                activity_type=ActivityTypeEnum.CREATED,
                title="Support Ticket Created",
                description=f"Ticket {ticket.ticket_number} was opened.",
                severity=SeverityEnum.INFO,
                status="Open",
                user_id=creator.id
            ))
            
        db.commit()
        print(f"Successfully seeded 50 Support Tickets.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding tickets: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_support_tickets()
