import os
import sys
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.inventory import PurchaseOrder

def fix_pos():
    db = SessionLocal()
    try:
        pos = db.query(PurchaseOrder).all()
        count = 0
        for po in pos:
            if po.tracking_id:
                # Give it a realistic tracking number like TRK-8492019482
                po.tracking_id = f"TRK-{random.randint(1000000000, 9999999999)}"
                count += 1
        db.commit()
        print(f"Fixed {count} tracking IDs.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_pos()
