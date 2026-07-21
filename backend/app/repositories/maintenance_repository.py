"""
Maintenance repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.maintenance import Maintenance
from app.models.vehicle import Vehicle


class MaintenanceRepository:
    """Repository for maintenance database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, maintenance_id: UUID) -> Optional[Maintenance]:
        """Get maintenance by ID."""
        return self.db.query(Maintenance).filter(
            Maintenance.id == maintenance_id
        ).first()

    def get_by_number(self, maintenance_number: str) -> Optional[Maintenance]:
        """Get maintenance by maintenance number."""
        return self.db.query(Maintenance).filter(
            Maintenance.maintenance_number == maintenance_number
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Maintenance], int]:
        """
        Get all maintenance records with optional filters.

        Returns:
            Tuple of (maintenance list, total count)
        """
        query = self.db.query(Maintenance)

        # Apply filters
        if status:
            query = query.filter(Maintenance.status == status)

        if vehicle_id:
            query = query.filter(Maintenance.vehicle_id == vehicle_id)

        if priority:
            query = query.filter(Maintenance.priority == priority)

        if search:
            search_filter = or_(
                Maintenance.maintenance_number.ilike(f"%{search}%"),
                Maintenance.maintenance_type.ilike(f"%{search}%"),
                Maintenance.description.ilike(f"%{search}%"),
                Maintenance.assigned_technician.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        records = query.order_by(
            Maintenance.created_at.desc()
        ).offset(skip).limit(limit).all()

        return records, total

    def create(self, maintenance_data: dict) -> Maintenance:
        """Create a new maintenance record."""
        maintenance = Maintenance(**maintenance_data)
        self.db.add(maintenance)
        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance

    def update(self, maintenance: Maintenance, update_data: dict) -> Maintenance:
        """Update an existing maintenance record."""
        for field, value in update_data.items():
            setattr(maintenance, field, value)

        self.db.commit()
        self.db.refresh(maintenance)
        return maintenance

    def delete(self, maintenance: Maintenance) -> None:
        """Delete a maintenance record."""
        self.db.delete(maintenance)
        self.db.commit()

    def count_by_status(self) -> dict:
        """Get count of maintenance records by status."""
        result = self.db.query(
            Maintenance.status,
            func.count(Maintenance.id).label('count')
        ).group_by(Maintenance.status).all()

        return {status: count for status, count in result}

    def get_active_maintenance_by_vehicle(
        self,
        vehicle_id: UUID
    ) -> Optional[Maintenance]:
        """Get active maintenance for a vehicle (In Progress)."""
        return self.db.query(Maintenance).filter(
            Maintenance.vehicle_id == vehicle_id,
            Maintenance.status == 'In Progress'
        ).first()

    def get_next_maintenance_number(self) -> str:
        """Generate next maintenance number (MNT-YYYY-NNNNN)."""
        year = date.today().year
        prefix = f"MNT-{year}-"

        # Get the last maintenance number for this year
        last_record = self.db.query(Maintenance).filter(
            Maintenance.maintenance_number.like(f"{prefix}%")
        ).order_by(Maintenance.maintenance_number.desc()).first()

        if last_record:
            last_seq = int(last_record.maintenance_number.replace(prefix, ""))
            next_seq = last_seq + 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:05d}"

    def get_maintenance_by_vehicle(
        self,
        vehicle_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Maintenance], int]:
        """Get maintenance records for a specific vehicle."""
        query = self.db.query(Maintenance).filter(
            Maintenance.vehicle_id == vehicle_id
        )

        if status:
            query = query.filter(Maintenance.status == status)

        total = query.count()
        records = query.order_by(
            Maintenance.created_at.desc()
        ).offset(skip).limit(limit).all()

        return records, total

    def get_scheduler_events(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        technician: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Maintenance]:
        """Get all maintenance events for the scheduler without pagination."""
        query = self.db.query(Maintenance)

        if start_date:
            query = query.filter(Maintenance.scheduled_date >= start_date)
        if end_date:
            query = query.filter(Maintenance.scheduled_date <= end_date)
            
        if status:
            if status == 'Overdue':
                query = query.filter(
                    Maintenance.scheduled_date < date.today(),
                    Maintenance.status.not_in(['Completed', 'Rejected'])
                )
            elif status == 'Scheduled':
                query = query.filter(Maintenance.status.in_(['Pending', 'Approved']))
            elif status == 'Cancelled':
                query = query.filter(Maintenance.status == 'Rejected')
            else:
                query = query.filter(Maintenance.status == status)
                
        if priority:
            query = query.filter(Maintenance.priority == priority)
            
        if vehicle_id:
            query = query.filter(Maintenance.vehicle_id == vehicle_id)
            
        if technician:
            query = query.filter(Maintenance.assigned_technician == technician)
            
        if search:
            search_filter = or_(
                Maintenance.maintenance_number.ilike(f"%{search}%"),
                Maintenance.maintenance_type.ilike(f"%{search}%"),
                Maintenance.description.ilike(f"%{search}%"),
                Maintenance.assigned_technician.ilike(f"%{search}%"),
                Maintenance.vehicle.has(Vehicle.vehicle_name.ilike(f"%{search}%")),
                Maintenance.vehicle.has(Vehicle.registration_number.ilike(f"%{search}%"))
            )
            query = query.filter(search_filter)

        return query.order_by(Maintenance.scheduled_date.asc(), Maintenance.start_time.asc()).all()
