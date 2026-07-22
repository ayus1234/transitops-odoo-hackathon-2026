import os
import sys
import datetime
import random
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.inventory import PurchaseOrder, ShipmentStatusEnum, ProcurementRequest

def fix_all_inventory():
    db = SessionLocal()
    try:
        now = datetime.datetime.now()
        
        # 1. Fix Procurement Requests missing suggested quantity
        requests = db.query(ProcurementRequest).filter(ProcurementRequest.suggested_quantity == None).all()
        r_count = 0
        for req in requests:
            req.suggested_quantity = req.required_quantity + random.randint(0, 10)
            r_count += 1
            
        # 2. Fix POs missing tracking IDs or delivery dates
        pos = db.query(PurchaseOrder).all()
        p_count = 0
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
            
            if updated:
                p_count += 1
        
        db.commit()
        print(f"Fixed {r_count} procurement requests and {p_count} purchase orders.")
    finally:
        db.close()

if __name__ == "__main__":
    fix_all_inventory()
