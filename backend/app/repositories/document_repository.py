"""
Document repository for database operations.
"""
from datetime import date, timedelta
from typing import Optional, List
from uuid import UUID
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentRepository:
    """Repository for document database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def create(self, document_data: DocumentCreate, created_by_id: Optional[UUID] = None) -> Document:
        """Create a new document record."""
        data_dict = document_data.model_dump()
        doc = Document(**data_dict, created_by=created_by_id)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def update(self, doc: Document, update_data: DocumentUpdate) -> Document:
        """Update an existing document."""
        data = update_data.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(doc, field, value)

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete(self, doc: Document) -> None:
        """Delete a document record."""
        self.db.delete(doc)
        self.db.commit()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        verification_state: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        driver_id: Optional[UUID] = None,
        maintenance_id: Optional[UUID] = None,
        vendor_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """Get paginated documents with filtering."""
        query = self.db.query(Document)

        if document_type:
            query = query.filter(Document.document_type == document_type)
        if status:
            query = query.filter(Document.status == status)
        if verification_state:
            query = query.filter(Document.verification_state == verification_state)

        if vehicle_id:
            query = query.filter(Document.vehicle_id == vehicle_id)
        if driver_id:
            query = query.filter(Document.driver_id == driver_id)
        if maintenance_id:
            query = query.filter(Document.maintenance_id == maintenance_id)
        if vendor_id:
            query = query.filter(Document.vendor_id == vendor_id)

        if search:
            search_filter = or_(
                Document.title.ilike(f"%{search}%"),
                Document.document_number.ilike(f"%{search}%"),
                Document.issuer.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        total = query.count()
        docs = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

        return docs, total

    def get_expiring_documents(self, threshold_days: int = 30) -> List[Document]:
        """
        Get active documents expiring within the threshold window.
        """
        today = date.today()
        threshold_date = today + timedelta(days=threshold_days)

        return (
            self.db.query(Document)
            .filter(
                Document.status == 'Active',
                Document.expiry_date.isnot(None),
                Document.expiry_date >= today,
                Document.expiry_date <= threshold_date
            )
            .order_by(Document.expiry_date.asc())
            .all()
        )

    def get_expired_documents(self) -> List[Document]:
        """Get documents that have passed their expiry date."""
        today = date.today()

        return (
            self.db.query(Document)
            .filter(
                Document.expiry_date.isnot(None),
                Document.expiry_date < today
            )
            .order_by(Document.expiry_date.desc())
            .all()
        )
