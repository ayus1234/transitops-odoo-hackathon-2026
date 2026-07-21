import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver

db = SessionLocal()

# Find some draft trips
draft_trips = db.query(Trip).filter(Trip.status == 'Draft').limit(10).all()

# Some realistic coordinates for US cities to scatter them
locations = [
    (34.0522, -118.2437), # Los Angeles
    (37.7749, -122.4194), # SF
    (36.1699, -115.1398), # Vegas
    (39.7392, -104.9903), # Denver
    (32.7767, -96.7970),  # Dallas
    (29.7604, -95.3698),  # Houston
    (41.8781, -87.6298),  # Chicago
    (33.7490, -84.3880),  # Atlanta
    (40.7128, -74.0060),  # NYC
    (42.3601, -71.0589)   # Boston
]

for i, trip in enumerate(draft_trips):
    trip.status = 'Dispatched'
    
    # Update the vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
    if vehicle:
        vehicle.status = 'On Trip'
        lat, lng = locations[i % len(locations)]
        # Add some random jitter
        vehicle.latitude = lat + random.uniform(-0.5, 0.5)
        vehicle.longitude = lng + random.uniform(-0.5, 0.5)
        
    # Update the driver
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
    if driver:
        driver.status = 'On Trip'
        if vehicle:
            driver.latitude = vehicle.latitude
            driver.longitude = vehicle.longitude

db.commit()
print(f"Successfully dispatched {len(draft_trips)} new trips with updated coordinates!")
db.close()
