"""
Expense repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.expense import Expense


class ExpenseRepository:
    """Repository for expense database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, expense_id: UUID) -> Optional[Expense]:
        """Get expense record by ID."""
        return self.db.query(Expense).filter(
            Expense.id == expense_id
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        expense_type: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        trip_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None
    ) -> tuple[List[Expense], int]:
        """
        Get all expense records with optional filters.

        Returns:
            Tuple of (expense list, total count)
        """
        query = self.db.query(Expense)

        # Apply filters
        if expense_type:
            query = query.filter(Expense.expense_type == expense_type)
            
        if vehicle_id:
            query = query.filter(Expense.vehicle_id == vehicle_id)
            
        if trip_id:
            query = query.filter(Expense.trip_id == trip_id)
            
        if status:
            query = query.filter(Expense.status == status)

        if start_date:
            query = query.filter(Expense.expense_date >= start_date)

        if end_date:
            query = query.filter(Expense.expense_date <= end_date)

        if search:
            search_filter = or_(
                Expense.description.ilike(f"%{search}%"),
                Expense.vendor_name.ilike(f"%{search}%"),
                Expense.receipt_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        records = query.order_by(
            Expense.expense_date.desc(),
            Expense.created_at.desc()
        ).offset(skip).limit(limit).all()

        return records, total

    def create(self, expense_data: dict) -> Expense:
        """Create a new expense record."""
        expense = Expense(**expense_data)
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def update(self, expense: Expense, update_data: dict) -> Expense:
        """Update an existing expense record."""
        for field, value in update_data.items():
            setattr(expense, field, value)

        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete(self, expense: Expense) -> None:
        """Delete an expense record."""
        self.db.delete(expense)
        self.db.commit()
