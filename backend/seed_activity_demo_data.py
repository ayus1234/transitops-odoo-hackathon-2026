import sys
import os
import random
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.activity import ActivityLog, ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip

def get_random_date_within_90_days():
    # Mostly recent
    weights = [
        (0, 1),      # Today
        (1, 7),      # Last 7 days
        (7, 30),     # Last 30 days
        (30, 90)     # Last 90 days
    ]
    prob = random.random()
    if prob < 0.3:
        range_min, range_max = weights[0]
    elif prob < 0.6:
        range_min, range_max = weights[1]
    elif prob < 0.85:
        range_min, range_max = weights[2]
    else:
        range_min, range_max = weights[3]
        
    days_ago = random.randint(range_min, range_max)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    return datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

def run():
    print("Initializing Database Session...")
    db = SessionLocal()
    
    users = db.query(User).all()
    vehicles = db.query(Vehicle).all()
    drivers = db.query(Driver).all()
    trips = db.query(Trip).all()
    
    user_ids = [u.id for u in users] if users else [None]
    vehicle_ids = [v.id for v in vehicles] if vehicles else [None]
    driver_ids = [d.id for d in drivers] if drivers else [None]
    trip_ids = [t.id for t in trips] if trips else [None]
    
    activities_to_create = []

    def add_activity(module, activity_type, severity, title, desc, status="Success", user_id=None, vehicle_id=None, driver_id=None, trip_id=None, count=1):
        for _ in range(count):
            act = ActivityLog(
                module=module,
                activity_type=activity_type,
                severity=severity,
                title=title,
                description=desc,
                status=status,
                user_id=user_id or random.choice(user_ids),
                vehicle_id=vehicle_id,
                driver_id=driver_id,
                trip_id=trip_id,
                ip_address=random.choice(["192.168.1.10", "10.0.0.5", "172.16.0.4", "203.0.113.1", None, None]),
                created_at=get_random_date_within_90_days()
            )
            activities_to_create.append(act)

    print("Generating Authentication Activities (30)...")
    add_activity(ModuleEnum.AUTHENTICATION, ActivityTypeEnum.LOGIN, SeverityEnum.INFO, "User Login Successful", "User logged into the enterprise portal.", count=25)
    add_activity(ModuleEnum.AUTHENTICATION, ActivityTypeEnum.LOGIN, SeverityEnum.CRITICAL, "Unauthorized access attempt", "Failed login attempt detected from unknown IP.", status="Failed", count=5)

    print("Generating Vehicle Activities (75)...")
    add_activity(ModuleEnum.VEHICLE, ActivityTypeEnum.CREATED, SeverityEnum.SUCCESS, "Vehicle TRK-1001 registered successfully", "New heavy-duty truck added to fleet.", vehicle_id=random.choice(vehicle_ids), count=15)
    add_activity(ModuleEnum.VEHICLE, ActivityTypeEnum.UPDATED, SeverityEnum.INFO, "Vehicle TRK-204 moved to Maintenance", "Status updated from Available to In Shop.", vehicle_id=random.choice(vehicle_ids), count=30)
    add_activity(ModuleEnum.VEHICLE, ActivityTypeEnum.SYSTEM, SeverityEnum.CRITICAL, "Vehicle failure", "Engine control module reported critical failure.", status="Failed", vehicle_id=random.choice(vehicle_ids), count=10)
    add_activity(ModuleEnum.VEHICLE, ActivityTypeEnum.SYSTEM, SeverityEnum.INFO, "Truck #402 arrived at Berlin Logistics Hub", "Geofence perimeter crossed successfully.", vehicle_id=random.choice(vehicle_ids), count=20)

    print("Generating Driver Activities (50)...")
    add_activity(ModuleEnum.DRIVER, ActivityTypeEnum.CREATED, SeverityEnum.SUCCESS, "Driver Profile Created", "Onboarded new driver to the platform.", driver_id=random.choice(driver_ids), count=10)
    add_activity(ModuleEnum.DRIVER, ActivityTypeEnum.ASSIGNED, SeverityEnum.INFO, "Driver Assigned to Vehicle", "Assigned for upcoming weekly routes.", driver_id=random.choice(driver_ids), count=30)
    add_activity(ModuleEnum.DRIVER, ActivityTypeEnum.SYSTEM, SeverityEnum.WARNING, "Driver license expires in 7 days", "Automated compliance warning triggered.", driver_id=random.choice(driver_ids), count=10)

    print("Generating Trip Activities (100)...")
    add_activity(ModuleEnum.TRIP, ActivityTypeEnum.CREATED, SeverityEnum.INFO, "Route Generated", "Standard logistics route mapped and verified.", trip_id=random.choice(trip_ids), count=30)
    add_activity(ModuleEnum.TRIP, ActivityTypeEnum.ASSIGNED, SeverityEnum.INFO, "Trip Dispatched", "Driver dispatched for delivery run.", trip_id=random.choice(trip_ids), count=30)
    add_activity(ModuleEnum.TRIP, ActivityTypeEnum.COMPLETED, SeverityEnum.SUCCESS, "Driver Sarah Jenkins completed Route #8812", "All waypoints hit and cargo delivered securely.", trip_id=random.choice(trip_ids), count=30)
    add_activity(ModuleEnum.TRIP, ActivityTypeEnum.CANCELLED, SeverityEnum.WARNING, "Trip Cancelled due to weather", "Route aborted by dispatcher.", status="Failed", trip_id=random.choice(trip_ids), count=10)

    print("Generating Maintenance Activities (80)...")
    add_activity(ModuleEnum.MAINTENANCE, ActivityTypeEnum.CREATED, SeverityEnum.WARNING, "Maintenance due", "Regular 10k mile service required.", vehicle_id=random.choice(vehicle_ids), count=30)
    add_activity(ModuleEnum.MAINTENANCE, ActivityTypeEnum.APPROVED, SeverityEnum.SUCCESS, "Maintenance approved for Vehicle VH-4921", "Purchase order for parts approved by management.", vehicle_id=random.choice(vehicle_ids), count=20)
    add_activity(ModuleEnum.MAINTENANCE, ActivityTypeEnum.COMPLETED, SeverityEnum.SUCCESS, "Brake replacement completed", "Vehicle cleared for operation.", vehicle_id=random.choice(vehicle_ids), count=20)
    add_activity(ModuleEnum.MAINTENANCE, ActivityTypeEnum.SYSTEM, SeverityEnum.CRITICAL, "Maintenance overdue", "Vehicle operating past safe service window.", vehicle_id=random.choice(vehicle_ids), count=10)

    print("Generating Fuel Activities (100)...")
    add_activity(ModuleEnum.FUEL, ActivityTypeEnum.CREATED, SeverityEnum.INFO, "Fuel Log Added", "Refueling recorded at terminal station.", vehicle_id=random.choice(vehicle_ids), count=85)
    add_activity(ModuleEnum.FUEL, ActivityTypeEnum.SYSTEM, SeverityEnum.WARNING, "Fuel efficiency dropped below threshold", "System detected irregular consumption rates.", vehicle_id=random.choice(vehicle_ids), count=15)

    print("Generating Expense Activities (75)...")
    add_activity(ModuleEnum.EXPENSE, ActivityTypeEnum.CREATED, SeverityEnum.INFO, "Toll Expense Submitted", "Driver submitted expense for highway toll.", driver_id=random.choice(driver_ids), count=40)
    add_activity(ModuleEnum.EXPENSE, ActivityTypeEnum.APPROVED, SeverityEnum.SUCCESS, "Fleet Manager approved operational expenses", "Weekly expense batch cleared for reimbursement.", count=25)
    add_activity(ModuleEnum.EXPENSE, ActivityTypeEnum.SYSTEM, SeverityEnum.WARNING, "Expense threshold reached", "Monthly maintenance budget exceeded 90%.", count=10)

    print("Generating Report Activities (50)...")
    add_activity(ModuleEnum.REPORTS, ActivityTypeEnum.CREATED, SeverityEnum.INFO, "Monthly KPI Report Generated", "System compiled monthly aggregate statistics.", count=20)
    add_activity(ModuleEnum.REPORTS, ActivityTypeEnum.EXPORTED, SeverityEnum.SUCCESS, "Expense report exported successfully", "PDF payload sent to user.", count=30)

    print("Generating Notification Activities (50)...")
    add_activity(ModuleEnum.NOTIFICATION, ActivityTypeEnum.SYSTEM, SeverityEnum.INFO, "Notification marked as read", "User cleared notification inbox.", count=50)

    print("Generating Quick Action Activities (40)...")
    add_activity(ModuleEnum.QUICK_ACTIONS, ActivityTypeEnum.SYSTEM, SeverityEnum.INFO, "Quick Action executed: Generate Fleet Report", "Action triggered from dashboard shortcut.", count=40)

    print("Generating Help Center Activities (25)...")
    add_activity(ModuleEnum.HELP_CENTER, ActivityTypeEnum.SYSTEM, SeverityEnum.INFO, "Help Center viewed", "User accessed documentation library.", count=15)
    add_activity(ModuleEnum.HELP_CENTER, ActivityTypeEnum.CREATED, SeverityEnum.INFO, "Support request submitted by Fleet Manager", "Ticket opened for ERP integration.", count=10)

    print("Generating Settings Activities (30)...")
    add_activity(ModuleEnum.SETTINGS, ActivityTypeEnum.UPDATED, SeverityEnum.INFO, "Organization timezone updated to Asia/Kolkata", "Global setting changed by admin.", count=20)
    add_activity(ModuleEnum.SETTINGS, ActivityTypeEnum.SYSTEM, SeverityEnum.CRITICAL, "System errors", "Background worker process failed.", status="Failed", count=10)

    print(f"Total Activities Generated in Memory: {len(activities_to_create)}")
    print("Committing to Database...")
    
    # Sort them purely for nice insertion, though db handles it.
    activities_to_create.sort(key=lambda x: x.created_at)
    
    # Bulk insert
    db.bulk_save_objects(activities_to_create)
    db.commit()
    print("[SUCCESS] Seed process completed successfully!")

if __name__ == "__main__":
    run()
