"""
Document service layer containing business logic.
"""
from datetime import datetime, date, timezone
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentVerifyRequest
from app.repositories.document_repository import DocumentRepository
from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.models.user import User


class DocumentService:
    """Service for document business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = DocumentRepository(db)

    def get_document(self, document_id: UUID) -> Document:
        """
        Get document by ID.

        Raises:
            NotFoundError: If document not found
        """
        doc = self.repository.get_by_id(document_id)
        if not doc:
            raise NotFoundError(f"Document with ID {document_id} not found")

        # Auto-update status to Expired if passed expiry date
        self._check_and_update_expiry_status(doc)
        return doc

    def get_documents(
        self,
        page: int = 1,
        page_size: int = 20,
        document_type: Optional[str] = None,
        status: Optional[str] = None,
        verification_state: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        driver_id: Optional[UUID] = None,
        maintenance_id: Optional[UUID] = None,
        vendor_id: Optional[UUID] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Document], int]:
        """Get paginated documents with filtering."""
        skip = (page - 1) * page_size
        docs, total = self.repository.get_all(
            skip=skip,
            limit=page_size,
            document_type=document_type,
            status=status,
            verification_state=verification_state,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            maintenance_id=maintenance_id,
            vendor_id=vendor_id,
            search=search
        )

        for d in docs:
            self._check_and_update_expiry_status(d)

        return docs, total

    def create_document(self, data: DocumentCreate, current_user: Optional[User] = None) -> Document:
        """Create a new document record."""
        # Auto-set status to Expired if initial expiry date is in the past
        doc = self.repository.create(data, created_by_id=current_user.id if current_user else None)
        self._check_and_update_expiry_status(doc)
        return doc

    def update_document(self, document_id: UUID, data: DocumentUpdate, current_user: Optional[User] = None) -> Document:
        """Update an existing document."""
        doc = self.get_document(document_id)
        updated = self.repository.update(doc, data)
        self._check_and_update_expiry_status(updated)
        return updated

    def verify_document(self, document_id: UUID, req: DocumentVerifyRequest, current_user: User) -> Document:
        """
        Verify or reject a document.

        Raises:
            NotFoundError: If document not found
        """
        doc = self.get_document(document_id)
        doc.verification_state = req.verification_state
        doc.verified_by = current_user.id
        doc.verified_at = datetime.now(timezone.utc)

        if req.notes:
            if doc.notes:
                doc.notes += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Verification ({req.verification_state}): {req.notes}"
            else:
                doc.notes = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Verification ({req.verification_state}): {req.notes}"

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def delete_document(self, document_id: UUID, current_user: Optional[User] = None) -> None:
        """Delete a document record."""
        doc = self.get_document(document_id)
        self.repository.delete(doc)

    def get_expiring_documents(self, threshold_days: int = 30) -> List[Document]:
        """Get documents expiring within the threshold (default 30 days)."""
        docs = self.repository.get_expiring_documents(threshold_days)
        for d in docs:
            self._check_and_update_expiry_status(d)
        return docs

    def get_expired_documents(self) -> List[Document]:
        """Get expired documents."""
        docs = self.repository.get_expired_documents()
        for d in docs:
            self._check_and_update_expiry_status(d)
        return docs

    def _check_and_update_expiry_status(self, doc: Document) -> None:
        """Helper to mark document status as Expired if passed expiry date."""
        if doc.expiry_date and doc.expiry_date < date.today() and doc.status == 'Active':
            doc.status = 'Expired'
            self.db.commit()
            self.db.refresh(doc)
