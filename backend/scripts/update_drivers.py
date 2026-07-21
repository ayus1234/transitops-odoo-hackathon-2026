import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.driver import Driver

def update_drivers():
    db = SessionLocal()
    try:
        # Get first 5 available drivers
        drivers = db.query(Driver).filter(Driver.status == 'Available').limit(5).all()
        for i, driver in enumerate(drivers):
            driver.status = 'Off Duty'
            print(f"Updated driver {driver.license_number} to Off Duty")
        
        db.commit()
        print(f"Successfully updated {len(drivers)} drivers to Off Duty.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_drivers()
