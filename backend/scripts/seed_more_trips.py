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

CITIES = [
    "Seattle", "Miami", "Boston", "Denver", 
    "Austin", "Atlanta", "Phoenix", "Portland",
    "Las Vegas", "San Diego", "Houston", "Philadelphia"
]

def seed_more_trips():
    db = SessionLocal()
    try:
        # Get all vehicles and drivers
        vehicles = db.query(Vehicle).all()
        drivers = db.query(Driver).all()
        
        if not vehicles or not drivers:
            print("No vehicles or drivers found.")
            return

        num_trips_to_create = min(20, len(vehicles), len(drivers))
        print(f"Creating {num_trips_to_create} more active trips...")

        admin_id = None
        from app.models.user import User
        admin = db.query(User).filter(User.email == "admin@transitops.com").first()
        if admin:
            admin_id = admin.id

        for i in range(num_trips_to_create):
            v = vehicles[i]
            d = drivers[i]
            
            origin = random.choice(CITIES)
            dest = random.choice([c for c in CITIES if c != origin])
            
            trip = Trip(
                trip_number=f"TRP-EXT-{random.randint(1000, 9999)}",
                vehicle_id=v.id,
                driver_id=d.id,
                source=origin,
                destination=dest,
                cargo_weight_kg=random.uniform(500, 5000),
                planned_distance_km=random.uniform(100, 1000),
                planned_departure=datetime.utcnow() - timedelta(hours=random.randint(1, 5)),
                planned_arrival=datetime.utcnow() + timedelta(hours=random.randint(1, 10)),
                status="Dispatched",
                actual_departure=datetime.utcnow() - timedelta(hours=random.randint(1, 5)),
                start_odometer_km=random.uniform(10000, 50000),
                route_information=f"Route from {origin} to {dest}",
                estimated_arrival_time=datetime.utcnow() + timedelta(hours=random.randint(1, 10)),
                created_by=admin_id
            )
            db.add(trip)
            
            # Update vehicle and driver status
            v.status = "On Trip"
            d.status = "On Trip"
            
            # Scatter coordinates slightly around main US cities roughly
            # Just randomizing coordinates broadly across the US
            v.latitude = random.uniform(30.0, 45.0)
            v.longitude = random.uniform(-120.0, -75.0)
            d.latitude = v.latitude
            d.longitude = v.longitude

        db.commit()
        print(f"Successfully created {num_trips_to_create} active trips!")

    except Exception as e:
        print(f"Error seeding trips: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_more_trips()
