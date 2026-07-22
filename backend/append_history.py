import uuid
import random
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryHistory, InventoryHistoryTypeEnum
from app.models.user import User

def append_history():
    db = SessionLocal()
    
    parts = db.query(InventoryItem).limit(10).all()
    user = db.query(User).first()
    
    if not parts:
        print("No parts found to generate history.")
        return
        
    history_logs = []
    
    for _ in range(15):
        part = random.choice(parts)
        
        # Decide action
        action_type = random.choice(list(InventoryHistoryTypeEnum))
        
        qty_changed = 0
        if action_type == InventoryHistoryTypeEnum.RESTOCK:
            qty_changed = random.randint(10, 50)
            part.quantity_available += qty_changed
        elif action_type == InventoryHistoryTypeEnum.RELEASE:
            qty_changed = -random.randint(1, 5)
            part.quantity_available += qty_changed # actually negative
        elif action_type == InventoryHistoryTypeEnum.ADJUSTMENT:
            qty_changed = random.choice([-2, -1, 1, 2])
            part.quantity_available += qty_changed
        elif action_type == InventoryHistoryTypeEnum.RESERVED:
            qty_changed = -random.randint(1, 4)
            part.quantity_reserved -= qty_changed # moving available to reserved
            part.quantity_available += qty_changed
            
        if part.quantity_available < 0:
            part.quantity_available = 0
            
        log = InventoryHistory(
            id=uuid.uuid4(),
            part_id=part.id,
            type=action_type,
            quantity_changed=qty_changed,
            previous_quantity=part.quantity_available - qty_changed,
            new_quantity=part.quantity_available,
            user_id=user.id if random.random() > 0.3 and user else None,
            reference_id=f"REF-{random.randint(1000, 9999)}" if action_type != InventoryHistoryTypeEnum.ADJUSTMENT else "Manual Adjust",
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5), hours=random.randint(1, 20))
        )
        
        history_logs.append(log)
    
    db.add_all(history_logs)
    db.commit()
    print(f"Successfully generated {len(history_logs)} inventory history records.")

if __name__ == "__main__":
    append_history()
