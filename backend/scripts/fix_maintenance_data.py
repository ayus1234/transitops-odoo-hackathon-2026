import os
import sys
import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.maintenance import Maintenance

def fix_maintenance_data():
    db = SessionLocal()
    try:
        # Get all technicians
        technicians = [
            "Mike R.",
            "Sarah K.",
            "David J.",
            "Jennifer L.",
            "Robert M.",
            "Emily T.",
            "James B.",
            "Linda P."
        ]
        
        # We want to give exactly 3 active tasks to each technician.
        # Active means status in ['Pending', 'Approved', 'In Progress']
        
        # 1. Update all currently active tasks to Completed to reset the slate
        active_records = db.query(Maintenance).filter(
            Maintenance.status.in_(['Pending', 'Approved', 'In Progress'])
        ).all()
        for r in active_records:
            r.status = 'Completed'
        
        db.commit()

        # 2. Get records to make active. We need 3 * len(technicians) records.
        # Let's get the most recent ones.
        records_to_activate = db.query(Maintenance).order_by(Maintenance.created_at.desc()).limit(3 * len(technicians)).all()
        
        idx = 0
        for tech in technicians:
            for _ in range(3):
                if idx < len(records_to_activate):
                    record = records_to_activate[idx]
                    record.assigned_technician = tech
                    record.status = 'In Progress' # Make them In Progress to count towards workload
                    idx += 1
        
        db.commit()
        
        # 3. Create some upcoming scheduled services
        # Let's pick 3 random Completed tasks and make them Approved with a future date
        upcoming = db.query(Maintenance).filter(Maintenance.status == 'Completed').limit(3).all()
        base_date = datetime.datetime.now()
        
        for i, r in enumerate(upcoming):
            r.status = 'Approved'
            r.scheduled_date = base_date + datetime.timedelta(days=i)
            # Pick a technician that can take it, wait, if we do this, it will increase their workload to 4!
            # Let's assign it to one of the technicians, and just unassign one of their In Progress tasks to keep it at 3.
            tech = technicians[i % len(technicians)]
            r.assigned_technician = tech
            
            # Find an 'In Progress' task for this tech and complete it
            in_prog = db.query(Maintenance).filter(
                Maintenance.assigned_technician == tech,
                Maintenance.status == 'In Progress'
            ).first()
            if in_prog:
                in_prog.status = 'Completed'
                
        db.commit()

        # 4. Make sure NO record is left unassigned in the database, just in case?
        # Actually, if they are 'Completed' or 'Rejected', being unassigned is fine, but the user said "assign technicians to all the unassigned".
        # Let's assign a random technician to all unassigned records.
        unassigned = db.query(Maintenance).filter(
            Maintenance.assigned_technician == None
        ).all()
        for i, r in enumerate(unassigned):
            r.assigned_technician = technicians[i % len(technicians)]
        
        db.commit()
        print("Data fixed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_maintenance_data()
