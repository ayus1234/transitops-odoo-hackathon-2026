import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.trip import Trip

db = SessionLocal()

sources = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata"]
destinations = ["Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore"]

trips = db.query(Trip).all()
updated_count = 0

for trip in trips:
    trip.source = random.choice(sources)
    trip.destination = random.choice(destinations)
    updated_count += 1

db.commit()
print(f"Successfully updated {updated_count} trips with Indian places!")
db.close()
