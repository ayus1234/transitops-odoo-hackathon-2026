import os
import sys
import random
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip

# Coordinates around San Francisco Bay Area
CENTER_LAT = 37.7749
CENTER_LNG = -122.4194

def generate_random_coordinate(center_lat, center_lng, radius_km=30):
    # Roughly 1 deg latitude = 111km
    import math
    radius_deg = radius_km / 111.0
    u = random.random()
    v = random.random()
    w = radius_deg * math.sqrt(u)
    t = 2 * math.pi * v
    lat_offset = w * math.cos(t)
    lng_offset = w * math.sin(t) / math.cos(math.radians(center_lat))
    return center_lat + lat_offset, center_lng + lng_offset

def seed_fleet_map():
    db = SessionLocal()
    try:
        vehicles = db.query(Vehicle).all()
        drivers = db.query(Driver).all()
        trips = db.query(Trip).all()
        
        if not vehicles:
            print("No vehicles found in the database. Please run seed_mock_data.py first.")
            return

        print(f"Seeding coordinates for {len(vehicles)} vehicles...")
        for v in vehicles:
            lat, lng = generate_random_coordinate(CENTER_LAT, CENTER_LNG, 40)
            v.latitude = lat
            v.longitude = lng
        
        print(f"Seeding coordinates for {len(drivers)} drivers...")
        for d in drivers:
            lat, lng = generate_random_coordinate(CENTER_LAT, CENTER_LNG, 40)
            d.latitude = lat
            d.longitude = lng
            
        print(f"Updating route information for {len(trips)} trips...")
        for t in trips:
            t.route_information = f"Route from {t.source} to {t.destination}"
            t.estimated_arrival_time = datetime.utcnow() + timedelta(hours=random.randint(1, 10))
            
        db.commit()
        print("Fleet map seeding complete!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_fleet_map()
