import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.vehicle import Vehicle

def set_statuses():
    db = SessionLocal()
    try:
        # Get a couple of Available vehicles
        vehicles = db.query(Vehicle).filter(Vehicle.status == "Available").all()
        
        if len(vehicles) >= 2:
            vehicles[0].status = "In Shop"
            vehicles[1].status = "Retired"
            
            db.commit()
            print("Successfully set 1 vehicle to In Shop and 1 to Retired!")
        else:
            print("Not enough available vehicles to change statuses.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    set_statuses()
