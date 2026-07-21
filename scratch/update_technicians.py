import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops"
os.environ["SECRET_KEY"] = "thisisasecretkeyforlocaldevelopmentonly123"

from app.core.database import SessionLocal
from app.models.maintenance import Maintenance

db = SessionLocal()

tech_names = [
    "Rahul K.", "Amit S.", "Vikram P.", "Suresh M.", "Rajesh D.",
    "Deepak V.", "Sunil R.", "Sanjay C.", "Manoj B.", "Ashok T."
]

records = db.query(Maintenance).all()
updated_count = 0

for r in records:
    if r.assigned_technician:
        r.assigned_technician = random.choice(tech_names)
        updated_count += 1

db.commit()
print(f"Successfully updated {updated_count} technician names to authentic Indian men names!")
db.close()
