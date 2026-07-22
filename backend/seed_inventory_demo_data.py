import os
import random
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, init_db
from app.models.inventory import (
    InventoryItem, ProcurementRequest, PurchaseOrder, InventoryHistory,
    PartStatusEnum, ProcurementStatusEnum, PriorityEnum, ShipmentStatusEnum, InventoryHistoryTypeEnum
)
from app.models.user import User
import uuid
from datetime import datetime, timedelta

def seed_data():
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@transitops.com").first()
        if not user:
            print("No admin user found.")
            return

        print("Clearing old inventory data...")
        db.query(InventoryHistory).delete()
        db.query(PurchaseOrder).delete()
        db.query(ProcurementRequest).delete()
        db.query(InventoryItem).delete()
        db.commit()

        print("Seeding expanded inventory data...")

        # 1. Expanded Inventory Items (15 items)
        parts_data = [
            ("Heavy Duty Brake Pads", "BP-900", 2, 10, 5, 45.50, "AutoParts Co", PartStatusEnum.CRITICAL_STOCK),
            ("Synthetic Engine Oil (5W-30)", "OIL-5W30-50G", 15, 5, 2, 250.00, "LubeTech", PartStatusEnum.IN_STOCK),
            ("Air Filter Type A", "AF-200A", 8, 15, 5, 12.75, "FilterKing", PartStatusEnum.LOW_STOCK),
            ("All-Weather Tire 22.5\"", "TR-225-AW", 0, 20, 8, 310.00, "TireMax", PartStatusEnum.OUT_OF_STOCK),
            ("Alternator 12V 150A", "ALT-12-150", 4, 3, 1, 185.00, "AutoParts Co", PartStatusEnum.IN_STOCK),
            ("Transmission Fluid (1 Gal)", "TF-GAL", 30, 10, 5, 22.00, "LubeTech", PartStatusEnum.IN_STOCK),
            ("Windshield Wipers 24\"", "WW-24", 5, 20, 5, 15.50, "VisionParts", PartStatusEnum.LOW_STOCK),
            ("Headlight Bulb H7", "HL-H7", 1, 10, 3, 8.25, "VisionParts", PartStatusEnum.CRITICAL_STOCK),
            ("Starter Motor 12V", "SM-12", 2, 2, 1, 210.00, "AutoParts Co", PartStatusEnum.IN_STOCK),
            ("Coolant Antifreeze (1 Gal)", "CA-GAL", 40, 15, 5, 18.00, "LubeTech", PartStatusEnum.IN_STOCK),
            ("Fuel Filter F-Series", "FF-F", 12, 15, 4, 25.00, "FilterKing", PartStatusEnum.LOW_STOCK),
            ("Battery 12V 1000CCA", "BAT-1000", 0, 5, 2, 180.00, "PowerCell", PartStatusEnum.OUT_OF_STOCK),
            ("Suspension Air Bag", "SUS-AB", 6, 8, 2, 350.00, "AutoParts Co", PartStatusEnum.LOW_STOCK),
            ("Exhaust Pipe Flex", "EX-FLEX", 8, 5, 2, 85.00, "ExhaustPro", PartStatusEnum.IN_STOCK),
            ("Cabin Air Filter", "CAF-100", 25, 10, 2, 10.50, "FilterKing", PartStatusEnum.IN_STOCK),
            ("Diesel Exhaust Fluid (55 Gal)", "DEF-55G", 0, 5, 2, 120.00, "ChemFluid", PartStatusEnum.INCOMING_SHIPMENT),
            ("Power Steering Fluid (1 Qt)", "PSF-1Q", 0, 20, 5, 8.50, "LubeTech", PartStatusEnum.INCOMING_SHIPMENT),
        ]
        
        parts = []
        for p in parts_data:
            parts.append(InventoryItem(
                name=p[0], part_number=p[1], quantity_available=p[2],
                minimum_stock_level=p[3], critical_stock_level=p[4],
                unit_cost=p[5], vendor=p[6], status=p[7]
            ))
            
        db.add_all(parts)
        db.commit()
        for p in parts: db.refresh(p)

        # 2. Procurement Requests (20 requests)
        reqs = [
            (parts[0].id, 20, 25, "AutoParts Co", PriorityEnum.URGENT, ProcurementStatusEnum.APPROVED),
            (parts[3].id, 40, 40, "TireMax", PriorityEnum.HIGH, ProcurementStatusEnum.SUBMITTED),
            (parts[2].id, 30, 50, "FilterKing", PriorityEnum.LOW, ProcurementStatusEnum.DRAFT),
            (parts[7].id, 15, 20, "VisionParts", PriorityEnum.HIGH, ProcurementStatusEnum.ORDERED),
            (parts[11].id, 10, 15, "PowerCell", PriorityEnum.URGENT, ProcurementStatusEnum.APPROVED),
            (parts[6].id, 50, 50, "VisionParts", PriorityEnum.MEDIUM, ProcurementStatusEnum.DELIVERED),
            (parts[12].id, 5, 5, "AutoParts Co", PriorityEnum.MEDIUM, ProcurementStatusEnum.SUBMITTED),
            (parts[1].id, 20, 20, "LubeTech", PriorityEnum.LOW, ProcurementStatusEnum.REJECTED),
            (parts[4].id, 10, 10, "AutoParts Co", PriorityEnum.MEDIUM, ProcurementStatusEnum.SUBMITTED),
            (parts[5].id, 15, 20, "LubeTech", PriorityEnum.LOW, ProcurementStatusEnum.APPROVED),
            (parts[8].id, 5, 5, "AutoParts Co", PriorityEnum.HIGH, ProcurementStatusEnum.DRAFT),
            (parts[9].id, 30, 40, "LubeTech", PriorityEnum.MEDIUM, ProcurementStatusEnum.ORDERED),
            (parts[10].id, 20, 25, "FilterKing", PriorityEnum.HIGH, ProcurementStatusEnum.DELIVERED),
            (parts[13].id, 10, 15, "ExhaustPro", PriorityEnum.URGENT, ProcurementStatusEnum.APPROVED),
            (parts[14].id, 50, 60, "FilterKing", PriorityEnum.LOW, ProcurementStatusEnum.SUBMITTED),
            (parts[2].id, 15, 15, "FilterKing", PriorityEnum.MEDIUM, ProcurementStatusEnum.REJECTED),
            (parts[7].id, 20, 20, "VisionParts", PriorityEnum.HIGH, ProcurementStatusEnum.APPROVED),
            (parts[1].id, 100, 120, "LubeTech", PriorityEnum.LOW, ProcurementStatusEnum.DELIVERED),
            (parts[3].id, 4, 4, "TireMax", PriorityEnum.URGENT, ProcurementStatusEnum.SUBMITTED),
            (parts[12].id, 10, 12, "AutoParts Co", PriorityEnum.MEDIUM, ProcurementStatusEnum.DRAFT),
        ]
        
        pr_objects = []
        for i, r in enumerate(reqs):
            pr = ProcurementRequest(
                procurement_id=f"PR-2026-0{i+1}1",
                part_id=r[0], requested_by_id=user.id,
                required_quantity=r[1], suggested_quantity=r[2],
                vendor=r[3], estimated_cost=parts[0].unit_cost * r[2], # Rough estimate
                priority=r[4], status=r[5],
                approved_by_id=user.id if r[5] in [ProcurementStatusEnum.APPROVED, ProcurementStatusEnum.ORDERED, ProcurementStatusEnum.DELIVERED] else None
            )
            pr_objects.append(pr)
            
        db.add_all(pr_objects)
        db.commit()
        for pr in pr_objects: db.refresh(pr)

        # 3. Purchase Orders (20 orders)
        pos = [
            (pr_objects[0].id, "AutoParts Co", 25, 1137.50, ShipmentStatusEnum.IN_TRANSIT, "TRK99823011"),
            (pr_objects[3].id, "VisionParts", 20, 165.00, ShipmentStatusEnum.DISPATCHED, "VP-099231"),
            (pr_objects[5].id, "VisionParts", 50, 775.00, ShipmentStatusEnum.DELIVERED, "VP-099200"),
            (pr_objects[4].id, "PowerCell", 15, 2700.00, ShipmentStatusEnum.PROCESSING, "PC-99120"),
            (pr_objects[1].id, "TireMax", 40, 12400.00, ShipmentStatusEnum.DELAYED, "TMX-9911-D"),
            (pr_objects[6].id, "AutoParts Co", 5, 1750.00, ShipmentStatusEnum.ORDERED, "AP-002931"),
            (pr_objects[7].id, "LubeTech", 20, 5000.00, ShipmentStatusEnum.ORDERED, "LT-109221"),
            (pr_objects[8].id, "AutoParts Co", 10, 2100.00, ShipmentStatusEnum.ORDERED, "AP-002945"),
            (pr_objects[9].id, "LubeTech", 15, 330.00, ShipmentStatusEnum.PROCESSING, "LT-109334"),
            (pr_objects[10].id, "AutoParts Co", 5, 925.00, ShipmentStatusEnum.DISPATCHED, "AP-003102"),
            (pr_objects[11].id, "LubeTech", 30, 540.00, ShipmentStatusEnum.IN_TRANSIT, "LT-109405"),
            (pr_objects[12].id, "FilterKing", 20, 500.00, ShipmentStatusEnum.DELIVERED, "FK-88219"),
            (pr_objects[13].id, "ExhaustPro", 10, 850.00, ShipmentStatusEnum.ORDERED, "EP-55910"),
            (pr_objects[14].id, "FilterKing", 50, 525.00, ShipmentStatusEnum.PROCESSING, "FK-88290"),
            (pr_objects[15].id, "FilterKing", 15, 191.25, ShipmentStatusEnum.DELAYED, "FK-88301"),
            (pr_objects[16].id, "VisionParts", 20, 165.00, ShipmentStatusEnum.ORDERED, "VP-099302"),
            (pr_objects[17].id, "LubeTech", 100, 25000.00, ShipmentStatusEnum.DELIVERED, "LT-109501"),
            (pr_objects[18].id, "TireMax", 4, 1240.00, ShipmentStatusEnum.ORDERED, "TMX-9920-A"),
            (pr_objects[19].id, "AutoParts Co", 10, 2100.00, ShipmentStatusEnum.PROCESSING, "AP-003204"),
            (pr_objects[2].id, "FilterKing", 30, 382.50, ShipmentStatusEnum.IN_TRANSIT, "FK-88410"),
        ]
        
        po_objects = []
        for i, po in enumerate(pos):
            po_objects.append(PurchaseOrder(
                po_number=f"PO-2026-8{i}91",
                procurement_request_id=po[0], vendor_name=po[1],
                quantity=po[2], cost=po[3],
                tracking_id=po[5], shipment_status=po[4],
                delivery_date=datetime.now() + timedelta(days=random.randint(2, 14))
            ))
            
        db.add_all(po_objects)

        # 4. History Logs (20 logs)
        logs = [
            (parts[1].id, InventoryHistoryTypeEnum.RESTOCK, 10, 5, 15, "LubeTech", 2500.00, "PO-2026-7011"),
            (parts[0].id, InventoryHistoryTypeEnum.RELEASE, -4, 6, 2, None, None, "MAINT-1029"),
            (parts[3].id, InventoryHistoryTypeEnum.RELEASE, -8, 8, 0, None, None, "MAINT-1033"),
            (parts[5].id, InventoryHistoryTypeEnum.ADJUSTMENT, -2, 32, 30, None, None, "AUDIT-01"),
            (parts[6].id, InventoryHistoryTypeEnum.RESTOCK, 50, 5, 55, "VisionParts", 775.00, "PO-2026-8291"),
            (parts[10].id, InventoryHistoryTypeEnum.RELEASE, -3, 15, 12, None, None, "MAINT-1045"),
            (parts[2].id, InventoryHistoryTypeEnum.RESERVED, 5, 3, 8, "FilterKing", 63.75, "MAINT-8822"),
            (parts[4].id, InventoryHistoryTypeEnum.RELEASE, -1, 5, 4, None, None, "MAINT-1048"),
            (parts[7].id, InventoryHistoryTypeEnum.ADJUSTMENT, -1, 2, 1, None, None, "AUDIT-02"),
            (parts[8].id, InventoryHistoryTypeEnum.RESERVED, 1, 3, 2, None, None, "MAINT-1052"),
            (parts[9].id, InventoryHistoryTypeEnum.RESTOCK, 20, 20, 40, "LubeTech", 360.00, "PO-2026-8911"),
            (parts[11].id, InventoryHistoryTypeEnum.RELEASE, -2, 2, 0, None, None, "MAINT-1060"),
            (parts[12].id, InventoryHistoryTypeEnum.RESTOCK, 4, 2, 6, "AutoParts Co", 1400.00, "PO-2026-9011"),
            (parts[13].id, InventoryHistoryTypeEnum.RELEASE, -1, 9, 8, None, None, "MAINT-1062"),
            (parts[14].id, InventoryHistoryTypeEnum.RESTOCK, 10, 15, 25, "FilterKing", 105.00, "PO-2026-9040"),
            (parts[15].id, InventoryHistoryTypeEnum.RESERVED, 1, 0, 1, "ChemFluid", 120.00, "MAINT-9122"),
            (parts[1].id, InventoryHistoryTypeEnum.RELEASE, -2, 17, 15, None, None, "MAINT-1065"),
            (parts[3].id, InventoryHistoryTypeEnum.ADJUSTMENT, 2, 0, 2, None, None, "AUDIT-03"),
            (parts[3].id, InventoryHistoryTypeEnum.RELEASE, -2, 2, 0, None, None, "MAINT-1066"),
            (parts[16].id, InventoryHistoryTypeEnum.RESTOCK, 5, 0, 5, "LubeTech", 42.50, "PO-2026-9201"),
        ]
        
        for l in logs:
            db.add(InventoryHistory(
                part_id=l[0], type=l[1], quantity_changed=l[2], previous_quantity=l[3], new_quantity=l[4],
                vendor=l[5], cost=l[6], user_id=user.id, reference_id=l[7]
            ))
            
        db.commit()

        print("Inventory data seeded successfully with expanded datasets!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
