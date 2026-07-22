import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.driver import Driver
from app.models.user import User
from app.models.maintenance import Maintenance

def fix_all_names():
    first_names = [
        "James", "Michael", "Robert", "John", "David", "William", "Richard", "Joseph", "Thomas", "Charles",
        "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
        "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle"
    ]
    
    last_initials = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    db = SessionLocal()
    try:
        # Update all Driver user names
        drivers = db.query(Driver).all()
        d_count = 0
        for driver in drivers:
            user = db.query(User).filter(User.id == driver.user_id).first()
            if user:
                # Only rename if it looks like test data or if we just want to rename all of them
                user.first_name = random.choice(first_names)
                user.last_name = random.choice(last_initials) + "."
                d_count += 1
        
        # Technician names are just strings in the Maintenance table
        # We should map existing test technician names to new realistic names so workloads group properly
        maintenances = db.query(Maintenance).all()
        m_count = 0
        tech_map = {}
        
        for m in maintenances:
            if m.assigned_technician:
                if m.assigned_technician not in tech_map:
                    tech_map[m.assigned_technician] = f"{random.choice(first_names)} {random.choice(last_initials)}."
                m.assigned_technician = tech_map[m.assigned_technician]
                m_count += 1

        db.commit()
        print(f"Fixed {d_count} driver users and {m_count} maintenance technician records.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_names()
