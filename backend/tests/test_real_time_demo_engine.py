import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.core.demo_engine import RealTimeDemoEngine
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.user import User
import uuid

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def engine():
    return RealTimeDemoEngine(interval_seconds=1)

def test_trip_completion_logic(engine, mock_db):
    """Test that trips past their ETA are completed and assets released."""
    sys_user = User(id=uuid.uuid4(), first_name="System", last_name="Admin")
    engine._get_system_user = MagicMock(return_value=sys_user)
    
    mock_trip = Trip(
        trip_number="TRP-1",
        estimated_arrival_time=datetime.now() - timedelta(minutes=5),
        status="Dispatched"
    )
    mock_trip.vehicle = Vehicle(status="On Trip", current_odometer_km=100.0)
    mock_trip.driver = Driver(status="On Trip")
    
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_trip]
    
    # Run the sub-engine
    with patch("app.core.demo_engine.activity_service") as mock_activity:
        engine._run_trip_engine(mock_db, datetime.now(), 12, sys_user)
        
        # Verify status updates
        assert mock_trip.status == "Completed"
        assert mock_trip.vehicle.status == "Available"
        assert mock_trip.driver.status == "Available"
        assert mock_trip.vehicle.current_odometer_km > 100.0
        
        # Verify activity was logged
        assert mock_activity.log_activity.called

def test_maintenance_engine(engine, mock_db):
    """Test that the engine autonomously schedules night maintenance."""
    sys_user = User(id=uuid.uuid4(), first_name="System", last_name="Admin")
    engine._get_system_user = MagicMock(return_value=sys_user)
    
    mock_vehicle = Vehicle(id="v1", registration_number="TRK-01", status="Available")
    
    # Mocking active maintenance query to return empty, and available vehicles to return our mock
    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [], # Active maintenance
        [mock_vehicle] # Idle vehicles
    ]
    
    # Force random to trigger
    with patch("random.random", return_value=0.01):
        engine._run_maintenance_engine(mock_db, datetime.now(), 23, sys_user)
        
        # Vehicle should be pushed to shop
        assert mock_vehicle.status == "In Shop"
        # Db add should have been called for Maintenance record + Notification
        assert mock_db.add.call_count >= 2

def test_fuel_and_expense_generation(engine, mock_db):
    """Test that the engine generates random expenses for active trips."""
    sys_user = User(id=uuid.uuid4())
    
    mock_trip = Trip(id="t1", vehicle_id="v1", status="Dispatched")
    mock_trip.vehicle = Vehicle(current_odometer_km=500.0)
    
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_trip]
    
    # Force random to trigger Fuel (random() < 0.3, then < 0.5)
    with patch("random.random", side_effect=[0.1, 0.1]):
        engine._run_fuel_and_expense_engine(mock_db, datetime.now(), sys_user)
        
        # Fuel log should be added
        assert mock_db.add.called
        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.__class__.__name__ == "Fuel"
        assert added_obj.trip_id == "t1"
