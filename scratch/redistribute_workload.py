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
    "Deepak V.", "Sunil R.", "Sanjay C.", "Manoj B.", "Ashok T.",
    "Ravi S.", "Harish V.", "Arun K.", "Navin D.", "Nitin M.",
    "Kishore J.", "Praveen L.", "Mukesh H.", "Sachin T.", "Yash R."
]

# We want to reduce workload so that no technician exceeds 4 tasks.
# Let's get all maintenance records that are assigned.
records = db.query(Maintenance).filter(Maintenance.assigned_technician != None).all()

# Group by technician to see current assignments
from collections import defaultdict
tech_workload = defaultdict(int)

# Re-assigning all records fairly
# Shuffle records to make it random
random.shuffle(records)

for r in records:
    # find a technician with < 3 tasks to be safe
    # If all have 3, we increase the threshold
    assigned = False
    for threshold in range(1, 5):
        available_techs = [t for t in tech_names if tech_workload[t] < threshold]
        if available_techs:
            chosen = random.choice(available_techs)
            r.assigned_technician = chosen
            tech_workload[chosen] += 1
            assigned = True
            break
    
    if not assigned:
        # fallback to unassigned
        r.assigned_technician = None

db.commit()
print("Successfully redistributed workloads to prevent overloading!")
for t, count in tech_workload.items():
    print(f"{t}: {count} tasks")
db.close()
