import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.trip import Trip
from app.models.fuel import FuelLog

db = SessionLocal()

trip = db.query(Trip).first()
if trip:
    print(f"Trip source: {trip.source}, dest: {trip.destination}")

fuel = db.query(FuelLog).first()
if fuel:
    print(f"Fuel location: {fuel.location}")

db.close()
