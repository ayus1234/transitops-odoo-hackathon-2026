"""
Document model for managing vehicle, driver, maintenance, and vendor documents/contracts.
"""
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from uuid import uuid4
from sqlalchemy import String, Integer, Date, DateTime, Text, ForeignKey, Index, func
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vehicle import Vehicle
    from app.models.driver import Driver
    from app.models.maintenance import Maintenance


DOCUMENT_TYPES = [
    'registration', 'insurance', 'fitness', 'pollution', 'permit',
    'licence', 'training_cert', 'warranty', 'lease_contract',
    'service_agreement', 'other'
]

DOCUMENT_STATUSES = ['Active', 'Expired', 'Revoked', 'Draft']
VERIFICATION_STATES = ['Unverified', 'Verified', 'Rejected']


class Document(Base):
    """
    Document model for document repository and compliance tracking.

    Can be associated with a Vehicle, Driver, Maintenance Log, or Vendor.
    Tracks expiration, verification state, and file metadata.
    """
    __tablename__ = "documents"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Document Metadata
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    document_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    issue_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True
    )

    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True
    )

    issuer: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # File Storage References
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    file_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    file_size_bytes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    # Status and Verification
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Active',
        index=True
    )

    verification_state: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='Unverified',
        index=True
    )

    verified_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Polymorphic Foreign Keys
    vehicle_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    driver_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    maintenance_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("maintenance_logs.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    vendor_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )

    # Audit FKs & Timestamps
    created_by: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=func.now(),
        nullable=False
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Relationships
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", lazy="joined", foreign_keys=[vehicle_id])
    driver: Mapped[Optional["Driver"]] = relationship("Driver", lazy="joined", foreign_keys=[driver_id])
    maintenance: Mapped[Optional["Maintenance"]] = relationship("Maintenance", lazy="select", foreign_keys=[maintenance_id])
    creator: Mapped[Optional["User"]] = relationship("User", lazy="select", foreign_keys=[created_by])
    verifier: Mapped[Optional["User"]] = relationship("User", lazy="select", foreign_keys=[verified_by])

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, type={self.document_type}, title={self.title}, status={self.status})>"

    @property
    def is_expired(self) -> bool:
        """Check if document has passed its expiry date."""
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days remaining until expiry date."""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days
