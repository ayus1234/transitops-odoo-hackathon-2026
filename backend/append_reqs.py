import os
import random
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.inventory import ProcurementRequest, ProcurementStatusEnum, PriorityEnum, InventoryItem
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == "admin@transitops.com").first()
parts = db.query(InventoryItem).all()

reqs = [
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
count = db.query(ProcurementRequest).count()
for i, r in enumerate(reqs):
    pr = ProcurementRequest(
        procurement_id=f"PR-2026-X{count+i+1:04d}",
        part_id=r[0], requested_by_id=user.id,
        required_quantity=r[1], suggested_quantity=r[2],
        vendor=r[3], estimated_cost=parts[0].unit_cost * r[2],
        priority=r[4], status=r[5],
        approved_by_id=user.id if r[5] in [ProcurementStatusEnum.APPROVED, ProcurementStatusEnum.ORDERED, ProcurementStatusEnum.DELIVERED] else None
    )
    pr_objects.append(pr)
    
db.add_all(pr_objects)
db.commit()
print(f"Added {len(pr_objects)} requests.")
