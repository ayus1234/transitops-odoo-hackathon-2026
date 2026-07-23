import sys
import os
import random
import uuid
from datetime import datetime, timedelta, date

# Setup path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

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
from app.models.settings import ApplicationSettings, OrganizationSettings

# Fix the random seed so that running this locally and on Vercel produces EXACTLY the same data
random.seed(42)

# ---------------------------------------------------------
# CONSTANTS & REALISTIC DATA POOLS
# ---------------------------------------------------------

INDIAN_CITIES = [
    ("Delhi", 28.7041, 77.1025),
    ("Mumbai", 19.0760, 72.8777),
    ("Bangalore", 12.9716, 77.5946),
    ("Hyderabad", 17.3850, 78.4867),
    ("Chennai", 13.0827, 80.2707),
    ("Pune", 18.5204, 73.8567),
    ("Kolkata", 22.5726, 88.3639),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Surat", 21.1702, 72.8311),
    ("Jaipur", 26.9124, 75.7873),
    ("Lucknow", 26.8467, 80.9462),
    ("Kanpur", 26.4499, 80.3319),
    ("Nagpur", 21.1458, 79.0882),
    ("Indore", 22.7196, 75.8577),
]

FIRST_NAMES = ["Aarav", "Vihaan", "Aditya", "Arjun", "Sai", "Rajesh", "Amit", "Rahul", "Vikram", "Sanjay", 
               "Priya", "Anjali", "Kavita", "Sneha", "Pooja", "Ramesh", "Suresh", "Manoj", "Dinesh", "Deepak"]
LAST_NAMES = ["Sharma", "Patel", "Singh", "Kumar", "Das", "Bose", "Gupta", "Nair", "Reddy", "Rao", 
              "Jain", "Verma", "Chauhan", "Yadav", "Pandey", "Iyer", "Pillai", "Mehta", "Deshmukh", "Joshi"]

VEHICLE_MANUFACTURERS = [
    ("Tata Motors", "Prima", "Truck"),
    ("Tata Motors", "Signa", "Truck"),
    ("Ashok Leyland", "Captain", "Truck"),
    ("Ashok Leyland", "Boss", "Truck"),
    ("Mahindra", "Blazo", "Truck"),
    ("Mahindra", "Furio", "Truck"),
    ("Volvo", "FH16", "Truck"),
    ("Volvo", "FMX", "Truck"),
    ("BharatBenz", "2823C", "Truck"),
    ("Eicher", "Pro 3000", "Truck"),
    ("Eicher", "Pro 6000", "Truck"),
    ("Force Motors", "Traveller", "Van"),
]

def random_date_past(days_back=90):
    return datetime(2026, 7, 24, 0, 0, 0) - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59))

def random_date_future(days_forward=30):
    return datetime(2026, 7, 24, 0, 0, 0) + timedelta(days=random.randint(1, days_forward), hours=random.randint(0, 23), minutes=random.randint(0, 59))

def run():
    db = SessionLocal()
    
    print("="*60)
    print("Enterprise Demo Data Seeder - TransitOps ERP")
    print("="*60)
    print("Connecting to database...")

    # Ensure Admin and Roles Exist
    print("Validating Roles & Admin User...")
    driver_role = db.query(Role).filter(Role.name == "Driver").first()
    fleet_manager_role = db.query(Role).filter(Role.name == "Fleet Manager").first()
    admin_role = db.query(Role).filter(Role.name == "Super Admin").first()
    
    administrator_role = db.query(Role).filter(Role.name == "Administrator").first()
    dispatcher_role = db.query(Role).filter(Role.name == "Dispatcher").first()
    maintenance_manager_role = db.query(Role).filter(Role.name == "Maintenance Manager").first()
    technician_role = db.query(Role).filter(Role.name == "Technician").first()
    safety_officer_role = db.query(Role).filter(Role.name == "Safety Officer").first()
    hr_role = db.query(Role).filter(Role.name == "HR/Operations").first()
    
    if not driver_role:
        driver_role = Role(name="Driver", permissions={"dashboard": ["read"], "trips": ["read", "update"], "vehicles": ["read"], "fuel": ["read", "create"], "maintenance": ["read"], "expenses": ["read", "create"]})
        db.add(driver_role)
    if not fleet_manager_role:
        fleet_manager_role = Role(name="Fleet Manager", permissions={"dashboard": ["read"], "vehicles": ["read", "create", "update", "delete", "export"], "drivers": ["read", "create", "update", "delete", "assign"], "trips": ["read", "create", "update", "delete", "export"], "maintenance": ["read", "manage", "approve"], "fuel": ["read", "export"], "reports": ["read", "export"], "inventory": ["read", "manage", "approve"]})
        db.add(fleet_manager_role)
    if not admin_role:
        admin_role = Role(name="Super Admin", permissions={"all": ["read", "create", "update", "delete"]})
        db.add(admin_role)
        
    if not administrator_role:
        administrator_role = Role(name="Administrator", permissions={"all": ["read", "create", "update", "delete"]})
        db.add(administrator_role)
    if not dispatcher_role:
        dispatcher_role = Role(name="Dispatcher", permissions={"trips": ["read", "create", "update", "assign", "dispatch"], "vehicles": ["read"], "drivers": ["read"]})
        db.add(dispatcher_role)
    if not maintenance_manager_role:
        maintenance_manager_role = Role(name="Maintenance Manager", permissions={"maintenance": ["read", "create", "update", "delete", "approve"], "vehicles": ["read", "update"], "inventory": ["read", "manage"]})
        db.add(maintenance_manager_role)
    if not technician_role:
        technician_role = Role(name="Technician", permissions={"maintenance": ["read", "update"], "vehicles": ["read"]})
        db.add(technician_role)
    if not safety_officer_role:
        safety_officer_role = Role(name="Safety Officer", permissions={"reports": ["read", "export"], "drivers": ["read", "update"], "vehicles": ["read"]})
        db.add(safety_officer_role)
    if not hr_role:
        hr_role = Role(name="HR/Operations", permissions={"drivers": ["read", "create", "update", "delete"], "users": ["read", "create", "update"]})
        db.add(hr_role)
        
    db.commit()

    admin_user = db.query(User).filter(User.email == "admin@transitops.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@transitops.com",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
    else:
        # Fix existing admin user
        admin_user.role_id = admin_role.id
        db.commit()

    # 1. SEED SETTINGS
    print("Seeding Settings...")
    app_settings = db.query(ApplicationSettings).filter(ApplicationSettings.key == "default").first()
    if not app_settings:
        app_settings = ApplicationSettings(
            key="default",
            app_name="TransitOps Enterprise ERP",
            timezone="Asia/Kolkata",
            date_format="DD-MM-YYYY",
            currency="INR",
            language="en"
        )
        db.add(app_settings)

    org_settings = db.query(OrganizationSettings).filter(OrganizationSettings.key == "default").first()
    if not org_settings:
        org_settings = OrganizationSettings(
            key="default",
            name="TransitOps Global Logistics",
            legal_name="TransitOps Logistics Pvt Ltd",
            email="contact@transitops.com",
            phone="+91-1800-TRANSIT",
            city="Bangalore",
            state="Karnataka",
            country="India",
            postal_code="560001"
        )
        db.add(org_settings)
    db.commit()

    # 2. SEED DRIVERS & USERS
    print("Seeding 50 Drivers...")
    users_created = []
    drivers_created = []
    
    existing_driver_count = db.query(Driver).count()
    drivers_to_create = max(0, 50 - existing_driver_count)
    
    for i in range(drivers_to_create):
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        email = f"driver.{fname.lower()}.{lname.lower()}{i+1000}@transitops.com"
        
        user = User(
            email=email,
            password_hash=get_password_hash("driver123"),
            first_name=fname,
            last_name=lname,
            phone_number=f"+9198{random.randint(10000000, 99999999)}",
            role_id=driver_role.id,
            is_active=True
        )
        db.add(user)
        db.flush()
        users_created.append(user)
        
        # Indian coordinates rough bounding box
        city_data = random.choice(INDIAN_CITIES)
        lat = city_data[1] + random.uniform(-0.1, 0.1)
        lon = city_data[2] + random.uniform(-0.1, 0.1)

        driver = Driver(
            user_id=user.id,
            license_number=f"MH{random.randint(10, 99)} {random.randint(2010, 2023)} {random.randint(1000000, 9999999)}",
            license_category=random.choice(["LMV", "HMV", "HGMV"]),
            license_issue_date=date(2026, 7, 24) - timedelta(days=random.randint(1000, 3000)),
            license_expiry_date=date(2026, 7, 24) + timedelta(days=random.randint(100, 1000)),
            date_of_birth=date(2026, 7, 24) - timedelta(days=random.randint(25*365, 55*365)),
            safety_score=random.uniform(75, 100),
            total_trips=random.randint(10, 200),
            status=random.choice(['Available', 'Available', 'On Trip', 'On Trip', 'Off Duty']),
            latitude=lat,
            longitude=lon
        )
        db.add(driver)
        drivers_created.append(driver)
    db.commit()
    
    # Add users for new roles
    print("Seeding users for additional roles...")
    
    # Also ensure there's a predictable Fleet Manager
    roles_to_seed = [
        (administrator_role, "administrator@transitops.com", "Admin", "adminpass2026"),
        (dispatcher_role, "dispatcher@transitops.com", "Dispatcher", "dispatch2026"),
        (maintenance_manager_role, "maintenance@transitops.com", "Maintenance", "maint2026"),
        (technician_role, "technician@transitops.com", "Technician", "tech2026"),
        (safety_officer_role, "safety@transitops.com", "Safety", "safety2026"),
        (hr_role, "hr@transitops.com", "HR", "hr2026"),
        (fleet_manager_role, "fleet@transitops.com", "Fleet", "fleet2026")
    ]
    
    for r, email, fname, password in roles_to_seed:
        if r:
            existing_user = db.query(User).filter(User.email == email).first()
            if not existing_user:
                lname = "User"
                user = User(
                    email=email,
                    password_hash=get_password_hash(password),
                    first_name=fname,
                    last_name=lname,
                    phone_number=f"+9198{random.randint(10000000, 99999999)}",
                    role_id=r.id,
                    is_active=True
                )
                db.add(user)
    db.commit()

    all_drivers = db.query(Driver).all()

    # 3. SEED VEHICLES
    print("Seeding 50 Vehicles...")
    vehicles_created = []
    
    existing_vehicle_count = db.query(Vehicle).count()
    vehicles_to_create = max(0, 50 - existing_vehicle_count)
    
    statuses = ['Available'] * 25 + ['On Trip'] * 15 + ['In Shop'] * 8 + ['Retired'] * 2
    
    for i in range(vehicles_to_create):
        make, model, vtype = random.choice(VEHICLE_MANUFACTURERS)
        city_data = random.choice(INDIAN_CITIES)
        lat = city_data[1] + random.uniform(-0.1, 0.1)
        lon = city_data[2] + random.uniform(-0.1, 0.1)
        
        v = Vehicle(
            registration_number=f"MH {random.randint(10, 40)} AB {random.randint(1000, 9999)}",
            vehicle_name=f"Fleet {vtype} {i+100}",
            vehicle_type=vtype,
            manufacturer=make,
            model=model,
            year=random.randint(2018, 2024),
            capacity_kg=random.uniform(2000, 25000),
            fuel_type=random.choice(["Diesel", "Diesel", "CNG", "Electric"]),
            current_odometer_km=random.uniform(5000, 300000),
            status=random.choice(statuses),
            latitude=lat,
            longitude=lon
        )
        db.add(v)
        vehicles_created.append(v)
    db.commit()
    
    all_vehicles = db.query(Vehicle).all()

    # 4. SEED TRIPS
    print("Seeding 120 Trips...")
    trips_created = []
    existing_trip_count = db.query(Trip).count()
    trips_to_create = max(0, 120 - existing_trip_count)
    
    trip_statuses = ['Completed'] * 60 + ['Dispatched'] * 35 + ['Draft'] * 20 + ['Cancelled'] * 5
    
    for i in range(trips_to_create):
        source_city = random.choice(INDIAN_CITIES)[0]
        dest_city = random.choice(INDIAN_CITIES)[0]
        while dest_city == source_city:
            dest_city = random.choice(INDIAN_CITIES)[0]
            
        status = random.choice(trip_statuses)
        
        start_dt = random_date_past(30) if status in ['Completed', 'Dispatched'] else random_date_future(15)
        end_dt = start_dt + timedelta(days=random.randint(1, 4), hours=random.randint(1, 12)) if status == 'Completed' else None
        
        t = Trip(
            trip_number=f"TRP-2026-{10000 + i}",
            vehicle_id=random.choice(all_vehicles).id if all_vehicles else None,
            driver_id=random.choice(all_drivers).id if all_drivers else None,
            source=source_city,
            destination=dest_city,
            cargo_weight_kg=random.uniform(500, 20000),
            planned_distance_km=random.uniform(200, 2500),
            planned_departure=start_dt,
            planned_arrival=start_dt + timedelta(days=random.randint(1, 4)),
            actual_departure=start_dt if status != 'Draft' else None,
            actual_arrival=end_dt,
            status=status
        )
        db.add(t)
        trips_created.append(t)
    db.commit()

    # 5. SEED MAINTENANCE (Scheduler Events)
    print("Seeding 80 Maintenance Jobs...")
    maintenance_created = []
    existing_maint_count = db.query(Maintenance).count()
    maint_to_create = max(0, 80 - existing_maint_count)
    
    maint_types = ["Oil Change", "Tire Replacement", "Brake Inspection", "Engine Overhaul", "AC Service", "Battery Check"]
    
    for i in range(maint_to_create):
        status = random.choice(['Completed', 'Completed', 'Pending', 'In Progress', 'Approved', 'Rejected'])
        sched_date = random_date_past(60) if status == 'Completed' else random_date_future(60)
        
        m = Maintenance(
            maintenance_number=f"MNT-2026-{1000 + i}",
            vehicle_id=all_vehicles[i % len(all_vehicles)].id if all_vehicles else None,
            maintenance_type=random.choice(maint_types),
            description=f"Standard {random.choice(maint_types).lower()} for vehicle health.",
            priority=random.choice(["Low", "Medium", "High", "Critical"]),
            status=status,
            scheduled_date=sched_date.date(),
            completed_date=sched_date.date() + timedelta(days=random.randint(1, 3)) if status == 'Completed' else None,
            assigned_technician=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            actual_cost=random.uniform(1000, 25000) if status == 'Completed' else None
        )
        db.add(m)
        maintenance_created.append(m)
    db.commit()

    # 6. SEED FUEL RECORDS
    print("Seeding 250 Fuel Records...")
    fuel_created = []
    existing_fuel_count = db.query(Fuel).count()
    fuel_to_create = max(0, 250 - existing_fuel_count)
    
    for i in range(fuel_to_create):
        qty = random.uniform(30, 200)
        cpl = random.uniform(85.0, 100.0)
        f = Fuel(
            vehicle_id=random.choice(all_vehicles).id if all_vehicles else None,
            fuel_type=random.choice(["Diesel", "Diesel", "CNG"]),
            quantity_liters=qty,
            cost_per_liter=cpl,
            total_cost=qty * cpl,
            odometer_reading=random.uniform(10000, 200000),
            refuel_date=random_date_past(90)
        )
        db.add(f)
        fuel_created.append(f)
    db.commit()

    # 7. SEED EXPENSES
    print("Seeding 150 Expenses...")
    expenses_created = []
    existing_expense_count = db.query(Expense).count()
    expense_to_create = max(0, 150 - existing_expense_count)
    
    for i in range(expense_to_create):
        e = Expense(
            expense_type=random.choice(["Toll", "Repair", "Fuel", "Maintenance", "Miscellaneous"]),
            amount=random.uniform(200, 5000),
            expense_date=random_date_past(90).date(),
            description="Operational expense during transit",
            status=random.choice(["Approved", "Approved", "Pending", "Rejected"]),
            recorded_by=admin_user.id
        )
        db.add(e)
        expenses_created.append(e)
    db.commit()

    # 8. SEED QUICK ACTIONS
    print("Seeding Quick Actions...")
    db.query(QuickAction).delete() # Reset Quick Actions for clean state
    actions = [
        {"name": "register_vehicle", "display_name": "Register Vehicle", "category": "Vehicles", "icon": "local_shipping", "route": "/vehicles/new", "permission_resource": "vehicles", "permission_action": "create", "description": "Add a new vehicle to the fleet.", "display_order": 1},
        {"name": "create_trip", "display_name": "Create Trip", "category": "Trips", "icon": "add_road", "route": "/trips/new", "permission_resource": "trips", "permission_action": "create", "description": "Plan a new trip.", "display_order": 2},
        {"name": "assign_driver", "display_name": "Assign Driver", "category": "Drivers", "icon": "assignment_ind", "route": "/drivers", "permission_resource": "drivers", "permission_action": "update", "description": "Assign a driver to a vehicle or trip.", "display_order": 3},
        {"name": "generate_report", "display_name": "Generate Report", "category": "Reports", "icon": "summarize", "route": "/reports", "permission_resource": "reports", "permission_action": "read", "description": "Generate standard reports.", "display_order": 4},
        {"name": "create_maintenance_record", "display_name": "Schedule Maintenance", "category": "Maintenance", "icon": "build", "route": "/maintenance/new", "permission_resource": "maintenance", "permission_action": "create", "description": "Schedule new maintenance.", "display_order": 5},
        {"name": "export_csv", "display_name": "Export Analytics", "category": "Reports", "icon": "csv", "route": "/reports", "permission_resource": "reports", "permission_action": "read", "description": "Export data to CSV.", "display_order": 6},
    ]
    # Adding more to reach around 40 if needed, but 40 unique actions is a lot.
    # We will generate permutations to hit the count.
    for category in ["Vehicles", "Drivers", "Trips", "Maintenance", "Fuel", "Expenses", "Reports", "Settings"]:
        for action in ["View", "Update", "Delete", "Audit", "Export"]:
            actions.append({
                "name": f"{action.lower()}_{category.lower()}",
                "display_name": f"{action} {category}",
                "category": category,
                "icon": "widgets",
                "route": f"/{category.lower()}",
                "permission_resource": category.lower(),
                "permission_action": "read",
                "description": f"{action} operation for {category}.",
                "display_order": len(actions) + 1
            })
            
    for act in actions[:40]: # strictly 40
        qa = QuickAction(**act)
        db.add(qa)
    db.commit()

    # 9. SEED SUPPORT TICKETS
    print("Seeding 50 Support Tickets...")
    existing_tickets = db.query(SupportTicket).count()
    tickets_to_create = max(0, 50 - existing_tickets)
    
    for i in range(tickets_to_create):
        t = SupportTicket(
            ticket_number=f"TKT-2026-{1000 + i}",
            created_by=admin_user.id,
            title=random.choice(["GPS Tracker Offline", "Dashboard Sync Error", "Unable to assign driver", "Fuel log mismatch", "Report generation failed"]),
            description="Detailed issue description provided by the user.",
            module_name=random.choice(["Vehicles", "Dashboard", "Drivers", "Fuel", "Reports"]),
            priority=random.choice(["Low", "Medium", "High", "Critical"]),
            category="Technical Issue",
            status=random.choice(["Open", "In Progress", "Resolved", "Closed"])
        )
        db.add(t)
    db.commit()

    # 10. SEED CUSTOM REPORTS
    print("Seeding 20 Custom Reports...")
    existing_reports = db.query(CustomReport).count()
    reports_to_create = max(0, 20 - existing_reports)
    
    for i in range(reports_to_create):
        cr = CustomReport(
            name=f"Enterprise {random.choice(['Fleet', 'Fuel', 'Maintenance', 'Driver', 'Financial'])} Analytics Q{random.randint(1, 4)}",
            description="Generated enterprise analytics report.",
            module=random.choice(["vehicles", "trips", "maintenance", "fuel", "expenses"]),
            selected_fields=["id", "status", "created_at"],
            created_by=admin_user.id,
            is_public=True
        )
        db.add(cr)
    db.commit()

    # 11. SEED NOTIFICATIONS
    print("Seeding 120 Notifications...")
    existing_notifs = db.query(Notification).count()
    notifs_to_create = max(0, 120 - existing_notifs)
    
    for i in range(notifs_to_create):
        category = random.choice(['Vehicles', 'Drivers', 'Trips', 'Maintenance', 'Fuel', 'Expenses'])
        priority = random.choice(['Low', 'Medium', 'High', 'Critical'])
        n_type = 'Info'
        if priority == 'Critical': n_type = 'Critical'
        elif priority == 'High': n_type = 'Warning'
        elif priority == 'Medium': n_type = 'Success'
        
        n = Notification(
            user_id=admin_user.id,
            title=f"Alert regarding {category}",
            description=f"This is an automated system alert for the {category} module.",
            type=n_type,
            priority=priority,
            category=category,
            module_name=category,
            is_read=random.choice([True, False])
        )
        db.add(n)
    db.commit()

    # 12. SEED ACTIVITY LOGS
    print("Seeding 400 Activity Logs...")
    existing_activity = db.query(ActivityLog).count()
    activities_to_create = max(0, 400 - existing_activity)
    
    modules = list(ModuleEnum)
    types = list(ActivityTypeEnum)
    severities = list(SeverityEnum)
    
    activities_batch = []
    for i in range(activities_to_create):
        mod = random.choice(modules)
        act = random.choice(types)
        activities_batch.append(ActivityLog(
            user_id=admin_user.id,
            module=mod,
            activity_type=act,
            title=f"{act.value} record in {mod.value}",
            description=f"User performed {act.value} operation on {mod.value} entity.",
            severity=random.choice(severities),
            status=random.choice(["Success", "Success", "Success", "Failed"]),
            ip_address=f"192.168.1.{random.randint(1, 255)}",
            created_at=random_date_past(30)
        ))
        
        if len(activities_batch) >= 100:
            db.add_all(activities_batch)
            db.commit()
            activities_batch = []
            
    if activities_batch:
        db.add_all(activities_batch)
        db.commit()

    print("\n" + "="*60)
    print("Database seeding completed successfully!")
    print("="*60)
    
    # OUTPUT SUMMARY
    print(f"Total Vehicles: {db.query(Vehicle).count()}")
    print(f"Total Drivers: {db.query(Driver).count()}")
    print(f"Total Trips: {db.query(Trip).count()}")
    print(f"Total Maintenance Jobs: {db.query(Maintenance).count()}")
    print(f"Total Fuel Records: {db.query(Fuel).count()}")
    print(f"Total Expenses: {db.query(Expense).count()}")
    print(f"Total Activity Logs: {db.query(ActivityLog).count()}")
    print(f"Total Notifications: {db.query(Notification).count()}")
    print(f"Total Quick Actions: {db.query(QuickAction).count()}")
    print(f"Total Support Tickets: {db.query(SupportTicket).count()}")
    print(f"Total Custom Reports: {db.query(CustomReport).count()}")
    
    db.close()

if __name__ == "__main__":
    run()
