import sys
import os
import random
from datetime import datetime, timedelta, date

# Uses DATABASE_URL from .env or system environment
os.environ['SECRET_KEY'] = 'testsecret'
sys.path.insert(0, os.path.abspath('backend'))

from app.core.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.models.user import User
from app.models.role import Role

def run():
    db = SessionLocal()
    
    print("Clearing old data...")
    db.query(Expense).delete()
    db.query(Fuel).delete()
    db.query(Maintenance).delete()
    db.query(Trip).delete()
    db.query(Vehicle).delete()
    db.query(Driver).delete()
    db.query(User).filter(User.email != "admin@transitops.com").delete(synchronize_session=False)
    db.commit()

    print("Seeding Vehicles...")
    vehicles = []
    for i in range(1, 21):
        v = Vehicle(
            vehicle_name=f"Fleet Truck {i}",
            vehicle_type=random.choice(["Heavy Duty", "Light Duty", "Van"]),
            manufacturer=random.choice(["Volvo", "Freightliner", "Peterbilt"]),
            model=f"Model-X{i}",
            year=random.randint(2018, 2024),
            registration_number=f"TRK-{1000+i}",
            capacity_kg=random.uniform(5000, 20000),
            fuel_type=random.choice(["Diesel", "Electric", "Hybrid"]),
            status=random.choice(["Available", "In Shop", "On Trip"]),
            current_odometer_km=random.uniform(10000, 150000),
            latitude=random.uniform(37.6, 37.9),
            longitude=random.uniform(-122.5, -122.1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(v)
        vehicles.append(v)
    db.commit()

    print("Seeding Drivers...")
    admin_user = db.query(User).filter(User.email == "admin@transitops.com").first()
    drivers = []
    
    first_names = ["Rahul", "Amit", "Vikram", "Suresh", "Ramesh", "Rajesh", "Deepak", "Sunil", "Anil", "Sanjay"]
    last_names = ["Kumar", "Sharma", "Singh", "Patel", "Gupta", "Yadav", "Verma", "Das", "Mishra", "Pandey"]
    
    for i in range(100, 125):
        # We ensure a more even distribution by linking i to the days offset
        days_offsets = [-10, -5, 2, 5, 15, 25, 100, 200, 300]
        chosen_days = days_offsets[i % len(days_offsets)]
        
        # Make exactly 1 out of 5 suspended
        driver_status = "Suspended" if i % 5 == 0 else random.choice(["Available", "On Trip", "Off Duty"])
        
        d = Driver(
            user_id=admin_user.id if i == 100 else None,
            license_number=f"LIC-{random.randint(100000, 999999)}",
            license_category="CDL-A",
            license_issue_date=date.today() - timedelta(days=1000),
            license_expiry_date=date.today() + timedelta(days=chosen_days),
            date_of_birth=date.today() - timedelta(days=365*30),
            safety_score=random.uniform(70, 100),
            status=driver_status,
            latitude=random.uniform(37.6, 37.9),
            longitude=random.uniform(-122.5, -122.1)
        )
        # We need unique users per driver
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        u = User(
            email=f"{fname.lower()}.{lname.lower()}{i}@transitops.com",
            password_hash="mock",
            first_name=fname,
            last_name=lname,
            role_id=db.query(Role).filter(Role.name=="Driver").first().id
        )
        db.add(u)
        db.flush()
        d.user_id = u.id
        db.add(d)
        drivers.append(d)
    db.commit()
    
    print("Seeding Trips...")
    for i in range(30):
        t = Trip(
            trip_number=f"TRP-{1000+i}",
            vehicle_id=random.choice(vehicles).id,
            driver_id=random.choice(drivers).id,
            source=random.choice(["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Pune", "Kolkata"]),
            destination=random.choice(["Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore"]),
            cargo_weight_kg=random.uniform(1000, 5000),
            planned_distance_km=random.uniform(100, 1000),
            planned_departure=datetime.utcnow(),
            planned_arrival=datetime.utcnow() + timedelta(days=2),
            status=random.choice(["Draft", "Dispatched", "Completed", "Cancelled"])
        )
        db.add(t)
    db.commit()

    print("Seeding Maintenance...")
    techs = [
        "Ravi S.", "Harish V.", "Arun K.", "Navin D.", "Nitin M.",
        "Rahul K.", "Amit S.", "Vikram P.", "Suresh M.", "Rajesh D.",
        "Deepak V.", "Sunil R.", "Sanjay C.", "Manoj B.", "Ashok T."
    ]
    tech_counts = {t: 0 for t in techs}

    for i in range(60):
        # Pick a tech that has fewer than 6 tasks, or None
        available_techs = [t for t in techs if tech_counts[t] < 6]
        
        # 10% chance to be unassigned
        if not available_techs or random.random() < 0.1:
            chosen_tech = None
        else:
            # force first tech to be overloaded by prioritizing them if they have < 6
            if "Mike R." in available_techs and tech_counts["Mike R."] < 6 and random.random() < 0.7:
                chosen_tech = "Mike R."
            elif "Jessica P." in available_techs and tech_counts["Jessica P."] < 6 and random.random() < 0.7:
                chosen_tech = "Jessica P."
            else:
                chosen_tech = random.choice(available_techs)
            tech_counts[chosen_tech] += 1

        m = Maintenance(
            maintenance_number=f"MNT-{1000+i}",
            vehicle_id=random.choice(vehicles).id,
            maintenance_type=random.choice(["Preventive", "Repair", "Inspection"]),
            description="Regular service",
            priority=random.choice(["High", "Medium", "Low"]),
            status=random.choice(["Pending", "Approved", "In Progress", "Completed"]),
            assigned_technician=chosen_tech,
            scheduled_date=date.today() + timedelta(days=random.randint(-10, 20)),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(m)
    db.commit()

    print("Seeding Fuel...")
    for i in range(15):
        f = Fuel(
            vehicle_id=random.choice(vehicles).id,
            fuel_type="Diesel",
            quantity_liters=random.uniform(50.0, 300.0),
            cost_per_liter=random.uniform(1.20, 1.80),
            total_cost=random.uniform(60.0, 500.0),
            odometer_reading=random.uniform(10000, 150000),
            refuel_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(f)
    db.commit()

    print("Seeding Expenses...")
    for i in range(10):
        e = Expense(
            expense_type=random.choice(["Fuel", "Maintenance", "Toll", "Miscellaneous"]),
            amount=random.uniform(50.0, 500.0),
            expense_date=date.today() - timedelta(days=random.randint(1, 30)),
            description="Operational expense",
            status=random.choice(["Pending", "Approved", "Rejected"]),
            recorded_by=admin_user.id
        )
        db.add(e)
    db.commit()

    print("Seeding Quick Actions...")
    from app.models.quick_action import QuickAction
    db.query(QuickAction).delete()
    
    actions = [
        # Vehicles
        {"name": "register_vehicle", "display_name": "Register Vehicle", "category": "Vehicles", "icon": "local_shipping", "route": "/vehicles/new", "permission_resource": "vehicles", "permission_action": "create", "description": "Add a new vehicle to the fleet.", "display_order": 1},
        {"name": "edit_vehicle", "display_name": "Edit Vehicle", "category": "Vehicles", "icon": "edit", "route": "/vehicles", "permission_resource": "vehicles", "permission_action": "update", "description": "Modify vehicle details.", "display_order": 2},
        {"name": "update_vehicle_status", "display_name": "Update Vehicle Status", "category": "Vehicles", "icon": "published_with_changes", "route": "/vehicles", "permission_resource": "vehicles", "permission_action": "update", "description": "Update the operational status of a vehicle.", "display_order": 3},
        {"name": "view_vehicle_details", "display_name": "View Vehicle Details", "category": "Vehicles", "icon": "visibility", "route": "/vehicles", "permission_resource": "vehicles", "permission_action": "read", "description": "View full specifications of a vehicle.", "display_order": 4},
        
        # Drivers
        {"name": "register_driver", "display_name": "Register Driver", "category": "Drivers", "icon": "person_add", "route": "/drivers/new", "permission_resource": "drivers", "permission_action": "create", "description": "Onboard a new driver.", "display_order": 5},
        {"name": "assign_driver", "display_name": "Assign Driver", "category": "Drivers", "icon": "assignment_ind", "route": "/drivers", "permission_resource": "drivers", "permission_action": "update", "description": "Assign a driver to a vehicle or trip.", "display_order": 6},
        {"name": "update_driver", "display_name": "Update Driver", "category": "Drivers", "icon": "manage_accounts", "route": "/drivers", "permission_resource": "drivers", "permission_action": "update", "description": "Update driver license and details.", "display_order": 7},
        
        # Trips
        {"name": "create_trip", "display_name": "Create Trip", "category": "Trips", "icon": "add_road", "route": "/trips/new", "permission_resource": "trips", "permission_action": "create", "description": "Plan a new trip.", "display_order": 8},
        {"name": "dispatch_trip", "display_name": "Dispatch Trip", "category": "Trips", "icon": "send", "route": "/trips", "permission_resource": "trips", "permission_action": "update", "description": "Dispatch a planned trip.", "display_order": 9},
        {"name": "complete_trip", "display_name": "Complete Trip", "category": "Trips", "icon": "check_circle", "route": "/trips", "permission_resource": "trips", "permission_action": "update", "description": "Mark a trip as completed.", "display_order": 10},
        {"name": "cancel_trip", "display_name": "Cancel Trip", "category": "Trips", "icon": "cancel", "route": "/trips", "permission_resource": "trips", "permission_action": "update", "description": "Cancel a scheduled trip.", "display_order": 11},
        {"name": "view_trip_details", "display_name": "View Trip Details", "category": "Trips", "icon": "route", "route": "/trips", "permission_resource": "trips", "permission_action": "read", "description": "View trip route and logs.", "display_order": 12},
        
        # Maintenance
        {"name": "create_maintenance_record", "display_name": "Create Maintenance Record", "category": "Maintenance", "icon": "build", "route": "/maintenance/new", "permission_resource": "maintenance", "permission_action": "create", "description": "Schedule new maintenance.", "display_order": 13},
        {"name": "start_maintenance", "display_name": "Start Maintenance", "category": "Maintenance", "icon": "play_arrow", "route": "/maintenance", "permission_resource": "maintenance", "permission_action": "update", "description": "Begin maintenance work.", "display_order": 14},
        {"name": "complete_maintenance", "display_name": "Complete Maintenance", "category": "Maintenance", "icon": "done_all", "route": "/maintenance", "permission_resource": "maintenance", "permission_action": "update", "description": "Finish vehicle maintenance.", "display_order": 15},
        {"name": "view_maintenance_schedule", "display_name": "View Maintenance Schedule", "category": "Maintenance", "icon": "calendar_month", "route": "/maintenance", "permission_resource": "maintenance", "permission_action": "read", "description": "View upcoming maintenance.", "display_order": 16},
        
        # Fuel
        {"name": "add_fuel_entry", "display_name": "Add Fuel Entry", "category": "Fuel", "icon": "local_gas_station", "route": "/fuel/new", "permission_resource": "fuel", "permission_action": "create", "description": "Log a refueling event.", "display_order": 17},
        {"name": "view_fuel_analytics", "display_name": "View Fuel Analytics", "category": "Fuel", "icon": "insights", "route": "/fuel", "permission_resource": "fuel", "permission_action": "read", "description": "Analyze fuel consumption.", "display_order": 18},
        
        # Expenses
        {"name": "add_expense", "display_name": "Add Expense", "category": "Expenses", "icon": "request_quote", "route": "/expenses/new", "permission_resource": "expenses", "permission_action": "create", "description": "Record an operational expense.", "display_order": 19},
        {"name": "approve_expense", "display_name": "Approve Expense", "category": "Expenses", "icon": "verified", "route": "/expenses", "permission_resource": "expenses", "permission_action": "update", "description": "Approve pending expenses.", "display_order": 20},
        {"name": "view_expense_analytics", "display_name": "View Expense Analytics", "category": "Expenses", "icon": "account_balance", "route": "/expenses", "permission_resource": "expenses", "permission_action": "read", "description": "View financial analytics.", "display_order": 21},
        
        # Reports
        {"name": "generate_report", "display_name": "Generate Report", "category": "Reports", "icon": "summarize", "route": "/reports", "permission_resource": "reports", "permission_action": "read", "description": "Generate standard reports.", "display_order": 22},
        {"name": "export_csv", "display_name": "Export CSV", "category": "Reports", "icon": "csv", "route": "/reports", "permission_resource": "reports", "permission_action": "read", "description": "Export data to CSV.", "display_order": 23},
        {"name": "export_pdf", "display_name": "Export PDF", "category": "Reports", "icon": "picture_as_pdf", "route": "/reports", "permission_resource": "reports", "permission_action": "read", "description": "Export data to PDF.", "display_order": 24},
        {"name": "create_custom_report", "display_name": "Create Custom Report", "category": "Reports", "icon": "query_stats", "route": "/custom-reports/new", "permission_resource": "custom_reports", "permission_action": "create", "description": "Build a custom analytics report.", "display_order": 25},
        
        # Dashboard
        {"name": "view_live_fleet_map", "display_name": "View Live Fleet Map", "category": "Dashboard", "icon": "map", "route": "/dashboard", "permission_resource": "dashboard", "permission_action": "read", "description": "View live tracking map.", "display_order": 26},
        {"name": "view_recent_activity", "display_name": "View Recent Activity", "category": "Dashboard", "icon": "history", "route": "/activity", "permission_resource": "activity", "permission_action": "read", "description": "View enterprise audit trail.", "display_order": 27},
        
        # Settings
        {"name": "create_user", "display_name": "Create User", "category": "Settings", "icon": "person_add", "route": "/settings/users/new", "permission_resource": "settings", "permission_action": "create", "description": "Create a new user account.", "display_order": 28},
        {"name": "assign_roles", "display_name": "Assign Roles", "category": "Settings", "icon": "admin_panel_settings", "route": "/settings/roles", "permission_resource": "settings", "permission_action": "update", "description": "Manage user permissions.", "display_order": 29},
        {"name": "update_organization_settings", "display_name": "Update Organization Settings", "category": "Settings", "icon": "business", "route": "/settings/organization", "permission_resource": "settings", "permission_action": "update", "description": "Configure company details.", "display_order": 30},
        
        # Notifications
        {"name": "open_notification_center", "display_name": "Open Notification Center", "category": "Notifications", "icon": "notifications", "route": "/notifications", "permission_resource": "notifications", "permission_action": "read", "description": "View system notifications.", "display_order": 31},
        
        # Help Center
        {"name": "open_documentation", "display_name": "Open Documentation", "category": "Help Center", "icon": "help", "route": "/help", "permission_resource": "help_center", "permission_action": "read", "description": "Access system documentation.", "display_order": 32}
    ]
    
    for act in actions:
        qa = QuickAction(**act)
        db.add(qa)
    db.commit()

    print("Database fully populated with Hackathon Demo Data!")
    
run()
