import os
from sqlalchemy import create_engine
from app.core.database import Base
from app.core.config import settings

# Ensure models are imported so they are registered with Base.metadata
from app.models.inventory import InventoryItem, ProcurementRequest, PurchaseOrder, InventoryHistory

def run():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Inventory tables synchronized successfully.")

if __name__ == "__main__":
    run()
