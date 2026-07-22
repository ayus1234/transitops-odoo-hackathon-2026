import os
import sys
import random
from datetime import date, time, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.maintenance import Maintenance
from app.models.vehicle import Vehicle
from app.models.user import User

VALID_MAINTENANCE_TYPES = [
    'Oil Change', 'Tire Replacement', 'Engine Repair',
    'Brake Service', 'Battery Replacement', 'Transmission Service',
    'AC Service', 'General Inspection', 'Body Repair', 'Other'
]
VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical']

FIRST_NAMES = ["Aarav", "Vihaan", "Aditya", "Arjun", "Sai", "Rajesh", "Amit", "Rahul", "Vikram", "Sanjay", "Priya", "Anjali", "Kavita", "Sneha", "Pooja", "Ramesh", "Suresh", "Manoj", "Dinesh", "Deepak"]
LAST_NAMES = ["Sharma", "Patel", "Singh", "Kumar", "Das", "Bose", "Gupta", "Nair", "Reddy", "Rao", "Jain", "Verma", "Chauhan", "Yadav", "Pandey", "Iyer", "Pillai", "Mehta", "Deshmukh", "Joshi"]


def seed_scheduler():
    db = SessionLocal()
    try:
        # Clear existing maintenance
        db.query(Maintenance).delete()
        
        vehicles = db.query(Vehicle).all()
        admin = db.query(User).filter(User.email == 'admin@transitops.com').first()
        
        if not vehicles or not admin:
            print("No vehicles or admin found. Seed those first.")
            return

        today = date.today()
        
        distribution = {
            'Scheduled': 15,
            'In Progress': 10,
            'Completed': 15,
            'Overdue': 5,
            'Cancelled': 5
        }
        
        count = 1
        for dist_status, qty in distribution.items():
            for _ in range(qty):
                v = random.choice(vehicles)
                priority = random.choice(VALID_PRIORITIES)
                if dist_status == 'Overdue' and random.random() < 0.5:
                    priority = 'Critical'
                    
                maintenance_type = random.choice(VALID_MAINTENANCE_TYPES)
                
                if dist_status == 'Scheduled':
                    status = random.choice(['Pending', 'Approved'])
                    sched_date = today + timedelta(days=random.randint(1, 30))
                elif dist_status == 'Overdue':
                    status = random.choice(['Pending', 'Approved'])
                    sched_date = today - timedelta(days=random.randint(1, 30))
                elif dist_status == 'In Progress':
                    status = 'In Progress'
                    sched_date = today
                elif dist_status == 'Completed':
                    status = 'Completed'
                    sched_date = today - timedelta(days=random.randint(5, 60))
                elif dist_status == 'Cancelled':
                    status = 'Rejected'
                    sched_date = today + timedelta(days=random.randint(-10, 10))
                else:
                    status = 'Pending'
                    sched_date = today
                
                start_h = random.randint(8, 16)
                duration = random.randint(30, 240) # 30 mins to 4 hours
                
                m = Maintenance(
                    maintenance_number=f"MNT-2026-{count:05d}",
                    vehicle_id=v.id,
                    maintenance_type=maintenance_type,
                    description=f"Scheduled {maintenance_type} for {v.vehicle_name}",
                    priority=priority,
                    assigned_technician=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    scheduled_date=sched_date,
                    start_time=time(hour=start_h, minute=0),
                    end_time=time(hour=start_h + duration//60, minute=duration%60),
                    estimated_duration=duration,
                    status=status,
                    created_by=admin.id
                )
                
                if status == 'Completed':
                    m.completed_date = sched_date + timedelta(days=random.randint(0, 2))
                    m.actual_cost = random.randint(50, 1000)
                    
                db.add(m)
                count += 1
                
        db.commit()
        print(f"Successfully seeded {count-1} maintenance jobs.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    seed_scheduler()
