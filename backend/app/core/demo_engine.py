import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import SessionLocal
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.models.notification import Notification
from app.models.help_center import SupportTicket
from app.models.user import User
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum

logger = logging.getLogger(__name__)

# Constants for simulation
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur"]
EXPENSE_TYPES = ["Toll", "Maintenance", "Repair", "Miscellaneous"]

class RealTimeDemoEngine:
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = interval_seconds
        self.is_running = False

    def _get_system_user(self, db: Session) -> Optional[User]:
        # Return the first admin or any user to associate records
        return db.query(User).first()

    def process_tick(self):
        """Executes one full iteration of the business simulation."""
        db = SessionLocal()
        try:
            now = datetime.now()
            hour = now.hour
            sys_user = self._get_system_user(db)
            if not sys_user:
                logger.warning("No system user found. Engine skipping tick.")
                return

            self._run_trip_engine(db, now, hour, sys_user)
            self._run_maintenance_engine(db, now, hour, sys_user)
            self._run_fuel_and_expense_engine(db, now, sys_user)
            self._run_support_ticket_engine(db, now, sys_user)
            self._run_gps_engine(db)

            db.commit()
        except Exception as e:
            logger.error(f"Demo Engine tick failed: {e}")
            db.rollback()
        finally:
            db.close()

    def _run_trip_engine(self, db: Session, now: datetime, hour: int, sys_user: User):
        # 1. Complete Due Trips
        active_trips = db.query(Trip).filter(Trip.status == "Dispatched").all()
        for trip in active_trips:
            # High completion probability if past ETA, or random chance for demo
            if trip.estimated_arrival_time and trip.estimated_arrival_time <= now or random.random() < 0.15:
                trip.status = "Completed"
                trip.actual_arrival = now
                
                if trip.vehicle:
                    trip.vehicle.status = "Available"
                    trip.vehicle.current_odometer_km = float(trip.vehicle.current_odometer_km or 0) + random.uniform(50.0, 300.0)
                if trip.driver:
                    # In evening, drivers go to Off Duty. During day, Available.
                    trip.driver.status = "Off Duty" if hour >= 17 or hour < 5 else "Available"

                # Log Activity & Notification
                self._notify(db, sys_user, f"Trip {trip.trip_number} Completed", f"Successfully arrived at {trip.destination}.", "Success", "Trips")
                activity_service.log_activity(db, ActivityCreate(module=ModuleEnum.TRIP, activity_type=ActivityTypeEnum.SYSTEM, title=f"Trip {trip.trip_number} Completed", description="Auto-completed by engine.", user_id=sys_user.id, severity=SeverityEnum.SUCCESS))

        # 2. Dispatch New Trips based on Time of Day Target
        # Morning: 12 active, Afternoon: 15 active, Night: 3 active
        target_trips = 12 if 6 <= hour < 10 else (15 if 10 <= hour < 17 else (6 if 17 <= hour < 21 else 3))
        current_active = len([t for t in active_trips if t.status == "Dispatched"])

        if current_active < target_trips and random.random() < 0.6:
            v = db.query(Vehicle).filter(Vehicle.status == "Available").first()
            d = db.query(Driver).filter(Driver.status == "Available").first()
            
            if v and d:
                origin = random.choice(CITIES)
                dest = random.choice([c for c in CITIES if c != origin])
                
                new_trip = Trip(
                    trip_number=f"TRP-{int(now.timestamp())}",
                    vehicle_id=v.id,
                    driver_id=d.id,
                    source=origin,
                    destination=dest,
                    planned_distance_km=random.uniform(50.0, 1000.0),
                    cargo_weight_kg=random.uniform(100.0, 2000.0),
                    planned_departure=now,
                    planned_arrival=now + timedelta(minutes=random.randint(5, 30)),
                    estimated_arrival_time=now + timedelta(minutes=random.randint(5, 30)),
                    status="Dispatched"
                )
                v.status = "On Trip"
                v.latitude = random.uniform(30.0, 47.0)
                v.longitude = random.uniform(-120.0, -75.0)
                d.status = "On Trip"
                db.add(new_trip)

                activity_service.log_activity(db, ActivityCreate(module=ModuleEnum.TRIP, activity_type=ActivityTypeEnum.CREATED, title=f"Autonomous Dispatch", description=f"{v.registration_number} dispatched.", user_id=sys_user.id, severity=SeverityEnum.INFO))

    def _run_maintenance_engine(self, db: Session, now: datetime, hour: int, sys_user: User):
        # Complete Maintenance
        active_m = db.query(Maintenance).filter(Maintenance.status == "In Progress").all()
        for m in active_m:
            if random.random() < 0.2:
                m.status = "Completed"
                m.completed_date = now.date()
                if m.vehicle:
                    m.vehicle.status = "Available"
                self._notify(db, sys_user, "Maintenance Completed", f"Vehicle {m.vehicle.registration_number if m.vehicle else ''} is ready.", "Info", "Maintenance")

        # Night time maintenance scheduling
        if hour >= 21 or hour < 5:
            idle_vehicles = db.query(Vehicle).filter(Vehicle.status == "Available").all()
            if idle_vehicles and random.random() < 0.1:
                v = random.choice(idle_vehicles)
                v.status = "In Shop"
                new_m = Maintenance(
                    maintenance_number=f"MNT-{int(now.timestamp())}",
                    vehicle_id=v.id,
                    maintenance_type="Routine Inspection",
                    description="Nightly auto-scheduled inspection.",
                    priority="Medium",
                    scheduled_date=now.date(),
                    status="In Progress",
                    estimated_cost=random.uniform(100.0, 500.0)
                )
                db.add(new_m)
                self._notify(db, sys_user, "Maintenance Started", f"Vehicle {v.registration_number} entered shop.", "Warning", "Maintenance")

    def _run_fuel_and_expense_engine(self, db: Session, now: datetime, sys_user: User):
        # Generate random fuel or expense for a vehicle currently On Trip
        active_trips = db.query(Trip).filter(Trip.status == "Dispatched").all()
        if active_trips and random.random() < 0.3:
            trip = random.choice(active_trips)
            
            # 50/50 chance for Fuel vs Expense
            if random.random() < 0.5:
                liters = random.uniform(20.0, 100.0)
                cost_per = random.uniform(1.2, 1.8)
                f = Fuel(
                    vehicle_id=trip.vehicle_id,
                    trip_id=trip.id,
                    fuel_type="Diesel",
                    quantity_liters=liters,
                    cost_per_liter=cost_per,
                    total_cost=liters * cost_per,
                    odometer_reading=trip.vehicle.current_odometer_km if trip.vehicle else 1000.0,
                    refuel_date=now,
                    recorded_by=sys_user.id
                )
                db.add(f)
            else:
                amt = random.uniform(10.0, 150.0)
                e = Expense(
                    expense_type=random.choice(EXPENSE_TYPES),
                    amount=amt,
                    expense_date=now.date(),
                    description="Autonomous operational expense.",
                    status="Approved",
                    vehicle_id=trip.vehicle_id,
                    trip_id=trip.id,
                    recorded_by=sys_user.id
                )
                db.add(e)

    def _run_support_ticket_engine(self, db: Session, now: datetime, sys_user: User):
        # Resolve existing tickets
        open_tickets = db.query(SupportTicket).filter(SupportTicket.status.in_(["Open", "In Progress"])).all()
        for t in open_tickets:
            if random.random() < 0.2:
                t.status = "Resolved"
                t.resolved_at = now
                self._notify(db, sys_user, "Ticket Resolved", f"Support Ticket {t.ticket_number} resolved.", "Success", "System")

        # Spawn new ticket rarely
        if random.random() < 0.05:
            new_t = SupportTicket(
                ticket_number=f"TKT-{int(now.timestamp())}",
                created_by=sys_user.id,
                title="Application Glitch Auto-Report",
                description="Simulated user issue.",
                module_name="Mobile App",
                priority=random.choice(["Low", "Medium", "High"]),
                category="Technical",
                status="Open"
            )
            db.add(new_t)

    def _run_gps_engine(self, db: Session):
        on_trip = db.query(Vehicle).filter(Vehicle.status == "On Trip").all()
        for v in on_trip:
            if v.latitude and v.longitude:
                # Keep vehicles roughly within the US bounds, nudge them slightly
                lat_nudge = random.uniform(-0.1, 0.1)
                lon_nudge = random.uniform(-0.1, 0.1)
                v.latitude = max(25.0, min(float(v.latitude) + lat_nudge, 49.0))
                v.longitude = max(-125.0, min(float(v.longitude) + lon_nudge, -65.0))

    def _notify(self, db: Session, user: User, title: str, desc: str, type_val: str, cat: str):
        n = Notification(
            user_id=user.id,
            title=title,
            description=desc,
            type=type_val,
            priority="Medium",
            category=cat
        )
        db.add(n)

    async def run(self):
        self.is_running = True
        logger.info(f"Real-Time Enterprise Demo Engine started. Interval: {self.interval_seconds}s")
        while self.is_running:
            try:
                await asyncio.sleep(self.interval_seconds)
                self.process_tick()
            except asyncio.CancelledError:
                self.is_running = False
                logger.info("Real-Time Enterprise Demo Engine stopped.")
                break
            except Exception as e:
                logger.error(f"Engine Loop Error: {e}")
                await asyncio.sleep(5)

async def start_demo_engine():
    engine = RealTimeDemoEngine(interval_seconds=30)
    await engine.run()
