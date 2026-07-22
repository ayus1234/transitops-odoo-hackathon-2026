import os
import sys
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.maintenance import Maintenance

def seed_critical_alert():
    db = SessionLocal()
    try:
        # Find the vehicle that is "In Shop"
        vehicle = db.query(Vehicle).filter(Vehicle.status == "In Shop").first()
        
        if not vehicle:
            # If no vehicle is In Shop, just pick the first one
            vehicle = db.query(Vehicle).first()
            vehicle.status = "In Shop"
        
        # Create a critical maintenance record
        m = Maintenance(
            maintenance_number=f"MNT-CRIT-{int(datetime.now().timestamp())}",
            vehicle_id=vehicle.id,
            maintenance_type="Engine Failure",
            description="Critical engine failure detected while on route.",
            priority="Critical",
            scheduled_date=datetime.now().date(),
            status="In Progress",
            estimated_cost=5000.00
        )
        db.add(m)
        db.commit()
        print(f"Successfully created a Critical Maintenance alert for vehicle {vehicle.registration_number}!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_critical_alert()
