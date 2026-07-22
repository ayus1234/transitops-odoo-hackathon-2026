import os
import sys
import datetime
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.inventory import PurchaseOrder, ShipmentStatusEnum

def fix_all_pos():
    db = SessionLocal()
    try:
        now = datetime.datetime.now()
        pos = db.query(PurchaseOrder).all()
        count = 0
        for po in pos:
            updated = False
            # Ensure all delivered POs have delivery dates and tracking IDs
            if po.shipment_status == ShipmentStatusEnum.DELIVERED:
                if not po.delivery_date:
                    po.delivery_date = po.order_date + datetime.timedelta(days=random.randint(1, 5)) if po.order_date else now - datetime.timedelta(days=2)
                    updated = True
                if not po.tracking_id or po.tracking_id == "--":
                    po.tracking_id = f"TRK-{random.randint(1000000000, 9999999999)}"
                    updated = True
            
            # Ensure in_transit / dispatched POs have tracking IDs
            if po.shipment_status in [ShipmentStatusEnum.IN_TRANSIT, ShipmentStatusEnum.DISPATCHED, ShipmentStatusEnum.PROCESSING]:
                if not po.tracking_id or po.tracking_id == "--":
                    po.tracking_id = f"TRK-{random.randint(1000000000, 9999999999)}"
                    updated = True

            # Also ensure all tracking IDs are exactly in the new 10-digit format if they don't look like it
            # But the previous script already fixed the ones that HAD tracking IDs.
            
            if updated:
                count += 1
        
        db.commit()
        print(f"Fixed {count} purchase orders missing delivery dates or tracking IDs.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_pos()
