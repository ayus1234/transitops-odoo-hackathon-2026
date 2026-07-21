import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.core.database import SessionLocal
from app.models.driver import Driver

def run():
    db = SessionLocal()
    drivers = db.query(Driver).all()
    
    random.shuffle(drivers)
    
    # 1. Set some active drivers
    for d in drivers[:15]:
        if d.status != "Suspended":
            d.status = "On Trip"
            
    # 2. Lower safety score for a few drivers to trigger alerts (<75)
    for d in drivers[-5:]:
        d.safety_score = round(random.uniform(55.0, 74.0), 2)
        
    db.commit()
    print("Updated drivers: 15 On Trip, 5 with low safety scores for alerts.")

if __name__ == "__main__":
    run()
