import sys
import os
import random
import uuid
import time
from datetime import datetime, timedelta, date

# Setup path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.models.activity import ActivityLog, ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.notification import Notification
from app.models.help_center import SupportTicket
from app.models.quick_action import QuickAction
from app.models.custom_report import CustomReport
from app.models.inventory import (
    InventoryItem, ProcurementRequest, PurchaseOrder, InventoryHistory,
    PartStatusEnum, ProcurementStatusEnum, PriorityEnum, ShipmentStatusEnum, InventoryHistoryTypeEnum
)
from app.models.settings import ApplicationSettings, OrganizationSettings

def random_date_past(days_back=365):
    return datetime.utcnow() - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59))

def random_date_future(days_forward=180):
    return datetime.utcnow() + timedelta(days=random.randint(1, days_forward), hours=random.randint(0, 23), minutes=random.randint(0, 59))

def batch_insert(db, objects, batch_size=1000):
    total = len(objects)
    for i in range(0, total, batch_size):
        db.add_all(objects[i:i+batch_size])
        db.commit()
        print(f"  Inserted {min(i+batch_size, total)}/{total}")

def run():
    print("=====================================================")
    print("      ENTERPRISE DATASET GENERATOR - TRANSITOPS      ")
    print("=====================================================")
    start_time = time.time()
    
    RUN_ID = str(uuid.uuid4())[:8]
    print(f"Run ID: {RUN_ID}")
    
    db = SessionLocal()
    
    # 1. Base Setup (Admin and Roles)
    print("Setting up Roles & Admin User...")
    driver_role = db.query(Role).filter(Role.name == "Driver").first()
    fleet_manager_role = db.query(Role).filter(Role.name == "Fleet Manager").first()
    
    if not driver_role:
        driver_role = Role(name="Driver", permissions={})
        db.add(driver_role)
    if not fleet_manager_role:
        fleet_manager_role = Role(name="Fleet Manager", permissions={})
        db.add(fleet_manager_role)
    db.commit()

    admin_user = db.query(User).filter(User.email == "admin@transitops.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@transitops.com",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role_id=fleet_manager_role.id,
            is_active=True
        )
        db.add(admin_user)
        db.commit()

    # Targets
    NUM_VEHICLES = 500
    NUM_DRIVERS = 500
    NUM_TRIPS = 2000
    NUM_MAINTENANCE = 1000
    NUM_INVENTORY_ITEMS = 3000
    NUM_PURCHASE_ORDERS = 500
    NUM_NOTIFICATIONS = 5000
    NUM_ACTIVITY_LOGS = 10000
    NUM_TICKETS = 1000
    NUM_REPORTS = 500

    print("\n--- Generating Drivers ---")
    users = []
    drivers = []
    pwd_hash = get_password_hash("password123")
    for i in range(NUM_DRIVERS):
        uid = uuid.uuid4()
        users.append(User(
            id=uid,
            email=f"driver.ent.{RUN_ID}.{i}@transitops.com",
            password_hash=pwd_hash,
            first_name="Driver",
            last_name=f"Number{i}",
            role_id=driver_role.id,
            is_active=True
        ))
        drivers.append(Driver(
            user_id=uid,
            license_number=f"DL-{RUN_ID}-{random.randint(100000, 999999)}",
            license_category=random.choice(["LMV", "HMV", "HGMV"]),
            license_issue_date=date.today() - timedelta(days=random.randint(1000, 3000)),
            license_expiry_date=date.today() + timedelta(days=random.randint(100, 1000)),
            date_of_birth=date.today() - timedelta(days=random.randint(25*365, 55*365)),
            safety_score=random.uniform(75, 100),
            total_trips=random.randint(10, 500),
            status=random.choice(['Available', 'On Trip', 'Off Duty']),
            latitude=20.0 + random.uniform(-5, 5),
            longitude=77.0 + random.uniform(-5, 5)
        ))
    batch_insert(db, users, 1000)
    batch_insert(db, drivers, 1000)

    print("\n--- Generating Vehicles ---")
    vehicles = []
    for i in range(NUM_VEHICLES):
        vehicles.append(Vehicle(
            registration_number=f"MH-{RUN_ID}-{i}",
            vehicle_name=f"Enterprise Fleet {RUN_ID} {i}",
            vehicle_type=random.choice(["Heavy Duty", "Medium Duty", "Van"]),
            manufacturer="Enterprise Motors",
            model="Pro Series",
            year=random.randint(2015, 2024),
            capacity_kg=random.uniform(2000, 25000),
            fuel_type=random.choice(["Diesel", "CNG", "Electric"]),
            current_odometer_km=random.uniform(5000, 500000),
            status=random.choice(['Available', 'On Trip', 'In Shop', 'Retired']),
            latitude=20.0 + random.uniform(-5, 5),
            longitude=77.0 + random.uniform(-5, 5)
        ))
    batch_insert(db, vehicles, 1000)

    # Fetch IDs for relationships
    vehicle_ids = [v.id for v in db.query(Vehicle.id).all()]
    driver_ids = [d.id for d in db.query(Driver.id).all()]
    admin_id = admin_user.id

    print("\n--- Generating Trips ---")
    trips = []
    for i in range(NUM_TRIPS):
        status = random.choice(['Completed', 'Dispatched', 'Draft', 'Cancelled'])
        start_dt = random_date_past(30) if status in ['Completed', 'Dispatched'] else random_date_future(15)
        trips.append(Trip(
            trip_number=f"TRP-{RUN_ID}-{i}",
            vehicle_id=random.choice(vehicle_ids),
            driver_id=random.choice(driver_ids),
            source=f"City {random.randint(1, 100)}",
            destination=f"City {random.randint(101, 200)}",
            cargo_weight_kg=random.uniform(500, 20000),
            planned_distance_km=random.uniform(200, 2500),
            planned_departure=start_dt,
            planned_arrival=start_dt + timedelta(days=random.randint(1, 4)),
            status=status
        ))
    batch_insert(db, trips, 1000)

    print("\n--- Generating Maintenance Jobs ---")
    maintenances = []
    for i in range(NUM_MAINTENANCE):
        maintenances.append(Maintenance(
            maintenance_number=f"MNT-{RUN_ID}-{i}",
            vehicle_id=random.choice(vehicle_ids),
            maintenance_type=random.choice(["Oil Change", "Tire Replacement", "Brake Inspection", "Engine Overhaul"]),
            description=f"Enterprise maintenance task {i}",
            priority=random.choice(["Low", "Medium", "High", "Critical"]),
            status=random.choice(['Completed', 'Pending', 'In Progress', 'Approved', 'Rejected']),
            scheduled_date=random_date_past(180).date(),
            actual_cost=random.uniform(1000, 25000)
        ))
    batch_insert(db, maintenances, 1000)

    print("\n--- Generating Inventory Items ---")
    items = []
    for i in range(NUM_INVENTORY_ITEMS):
        qty = random.randint(0, 100)
        status = PartStatusEnum.IN_STOCK
        if qty == 0: status = PartStatusEnum.OUT_OF_STOCK
        elif qty < 5: status = PartStatusEnum.CRITICAL_STOCK
        
        items.append(InventoryItem(
            name=f"Enterprise Part {RUN_ID} {i}",
            part_number=f"ENT-{RUN_ID}-{i}",
            quantity_available=qty,
            minimum_stock_level=10,
            critical_stock_level=5,
            unit_cost=random.uniform(5.0, 500.0),
            vendor="Enterprise Supplies",
            status=status
        ))
    batch_insert(db, items, 1000)
    
    item_ids = [i.id for i in db.query(InventoryItem.id).all()]

    print("\n--- Generating Purchase Orders ---")
    requests = []
    orders = []
    for i in range(NUM_PURCHASE_ORDERS):
        req_id = uuid.uuid4()
        requests.append(ProcurementRequest(
            id=req_id,
            procurement_id=f"PR-{RUN_ID}-{i}",
            part_id=random.choice(item_ids),
            requested_by_id=admin_id,
            required_quantity=random.randint(10, 100),
            suggested_quantity=random.randint(10, 100),
            vendor="Enterprise Supplies",
            estimated_cost=random.uniform(100, 5000),
            priority=PriorityEnum.MEDIUM,
            status=ProcurementStatusEnum.APPROVED,
            approved_by_id=admin_id
        ))
        orders.append(PurchaseOrder(
            po_number=f"PO-{RUN_ID}-{i}",
            procurement_request_id=req_id,
            vendor_name="Enterprise Supplies",
            quantity=random.randint(10, 100),
            cost=random.uniform(100, 5000),
            tracking_id=f"TRK-{RUN_ID}-{i}",
            shipment_status=random.choice(list(ShipmentStatusEnum)),
            delivery_date=random_date_future(30)
        ))
    batch_insert(db, requests, 1000)
    batch_insert(db, orders, 1000)

    print("\n--- Generating Support Tickets ---")
    tickets = []
    for i in range(NUM_TICKETS):
        tickets.append(SupportTicket(
            ticket_number=f"TKT-{RUN_ID}-{i}",
            created_by=admin_id,
            title=f"Enterprise Ticket {RUN_ID} {i}",
            description="Mass generated ticket for load testing.",
            module_name=random.choice(["Vehicles", "Drivers", "Trips", "Maintenance"]),
            priority=random.choice(["Low", "Medium", "High", "Critical"]),
            category="Performance Test",
            status=random.choice(["Open", "In Progress", "Resolved", "Closed"])
        ))
    batch_insert(db, tickets, 1000)
    
    print("\n--- Generating Reports ---")
    reports = []
    for i in range(NUM_REPORTS):
        reports.append(CustomReport(
            name=f"Enterprise Report {RUN_ID} {i}",
            description="Mass generated report.",
            module=random.choice(["vehicles", "trips", "maintenance", "fuel", "expenses"]),
            selected_fields=["id", "status"],
            created_by=admin_id,
            is_public=True
        ))
    batch_insert(db, reports, 1000)

    print("\n--- Generating Notifications ---")
    notifs = []
    for i in range(NUM_NOTIFICATIONS):
        notifs.append(Notification(
            user_id=admin_id,
            title=f"Enterprise Notification {RUN_ID} {i}",
            description="Mass generated notification.",
            type=random.choice(['Info', 'Critical', 'Warning', 'Success']),
            priority=random.choice(['Low', 'Medium', 'High', 'Critical']),
            category=random.choice(['Vehicles', 'Drivers', 'Trips', 'Maintenance']),
            module_name="Test",
            is_read=random.choice([True, False])
        ))
    batch_insert(db, notifs, 1000)

    print("\n--- Generating Activity Logs ---")
    logs = []
    for i in range(NUM_ACTIVITY_LOGS):
        logs.append(ActivityLog(
            user_id=admin_id,
            module=random.choice(list(ModuleEnum)),
            activity_type=random.choice(list(ActivityTypeEnum)),
            title=f"Enterprise Activity {RUN_ID} {i}",
            description="Mass generated activity log.",
            severity=random.choice(list(SeverityEnum)),
            status="Success",
            ip_address="10.0.0.1",
            created_at=random_date_past(180)
        ))
    batch_insert(db, logs, 2000)

    db.close()
    
    elapsed = time.time() - start_time
    print("=====================================================")
    print(f"  ENTERPRISE DATASET GENERATED IN {elapsed:.2f}s")
    print("=====================================================")

if __name__ == "__main__":
    run()
