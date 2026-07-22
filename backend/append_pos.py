import uuid
from datetime import datetime, timedelta
import random

from app.core.database import SessionLocal
from app.models.inventory import ProcurementRequest, PurchaseOrder, ShipmentStatusEnum, ProcurementStatusEnum

def append_pos():
    db = SessionLocal()
    
    # Get some approved procurement requests to attach POs to
    reqs = db.query(ProcurementRequest).filter(ProcurementRequest.status == ProcurementStatusEnum.APPROVED).all()
    if not reqs:
        # If no approved requests, get some submitted ones and approve them
        reqs = db.query(ProcurementRequest).filter(ProcurementRequest.status == ProcurementStatusEnum.SUBMITTED).limit(5).all()
        for r in reqs:
            r.status = ProcurementStatusEnum.APPROVED
        db.commit()
    
    if not reqs:
        print("No procurement requests found to attach POs to.")
        return
        
    vendors = ["AutoParts Co", "LubeTech", "TireMax", "EngineWorks", "BrakeMasters"]
    statuses = [ShipmentStatusEnum.ORDERED, ShipmentStatusEnum.PROCESSING, ShipmentStatusEnum.ORDERED, ShipmentStatusEnum.DISPATCHED, ShipmentStatusEnum.IN_TRANSIT]
    
    new_pos = []
    
    for i, req in enumerate(reqs[:10]):
        # Check if PO already exists
        if db.query(PurchaseOrder).filter(PurchaseOrder.procurement_request_id == req.id).first():
            continue
            
        po = PurchaseOrder(
            id=uuid.uuid4(),
            po_number=f"PO-2026-{random.randint(1000, 9999)}",
            procurement_request_id=req.id,
            vendor_name=req.vendor or random.choice(vendors),
            quantity=req.required_quantity,
            cost=req.estimated_cost or round(random.uniform(50.0, 500.0), 2),
            order_date=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            delivery_date=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
            tracking_id=f"TRK{random.randint(100000000, 999999999)}",
            shipment_status=random.choice(statuses)
        )
        new_pos.append(po)
        
        # Also update the req status to ORDERED
        req.status = ProcurementStatusEnum.ORDERED
        
    if new_pos:
        db.add_all(new_pos)
        db.commit()
        print(f"Appended {len(new_pos)} new purchase orders.")
    else:
        print("No new POs needed.")
        
if __name__ == "__main__":
    append_pos()
