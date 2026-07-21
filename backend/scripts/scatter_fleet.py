import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.driver import Driver

def scatter_fleet():
    db = SessionLocal()
    try:
        vehicles = db.query(Vehicle).all()
        drivers = db.query(Driver).all()
        
        print(f"Scattering {len(vehicles)} vehicles and {len(drivers)} drivers across the US...")
        
        for v in vehicles:
            v.latitude = random.uniform(30.0, 47.0)
            v.longitude = random.uniform(-120.0, -75.0)
            
        for d in drivers:
            d.latitude = random.uniform(30.0, 47.0)
            d.longitude = random.uniform(-120.0, -75.0)

        db.commit()
        print("Successfully scattered all fleet coordinates!")

    except Exception as e:
        print(f"Error scattering fleet: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    scatter_fleet()
