import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.inventory import ProcurementRequest

def fix_reqs():
    db = SessionLocal()
    try:
        reqs = db.query(ProcurementRequest).all()
        count = 0
        for req in reqs:
            if not req.suggested_quantity:
                # Set suggested quantity slightly higher or equal to required quantity
                req.suggested_quantity = req.required_quantity + random.randint(0, 10)
                count += 1
        db.commit()
        print(f"Fixed {count} procurement requests.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_reqs()
