"""Add documents table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-28 18:12:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'documents',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('document_type', sa.String(50), nullable=False, index=True),
        sa.Column('document_number', sa.String(100), nullable=True, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True, index=True),
        sa.Column('issuer', sa.String(255), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_name', sa.String(255), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='Active', index=True),
        sa.Column('verification_state', sa.String(20), nullable=False, server_default='Unverified', index=True),
        sa.Column('verified_by', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('vehicle_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('driver_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('drivers.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('maintenance_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('maintenance_logs.id', ondelete='CASCADE'), nullable=True, index=True),
        sa.Column('vendor_id', sa.Uuid(as_uuid=True), nullable=True, index=True),
        sa.Column('created_by', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('documents')
