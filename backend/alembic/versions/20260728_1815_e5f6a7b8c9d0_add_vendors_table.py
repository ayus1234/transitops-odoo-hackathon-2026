"""Add vendors table and vendor_id FKs to procurement and purchase orders

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-28 18:15:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('vendor_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('contact_person', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True, index=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('categories', sa.JSON(), nullable=True),
        sa.Column('payment_terms', sa.String(100), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1', index=True),
        sa.Column('rating', sa.Numeric(3, 2), nullable=True, server_default='5.00'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 2. Add vendor_id FK to procurement_requests and purchase_orders
    op.add_column('procurement_requests', sa.Column('vendor_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True))
    op.add_column('purchase_orders', sa.Column('vendor_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True))


def downgrade() -> None:
    op.drop_column('purchase_orders', 'vendor_id')
    op.drop_column('procurement_requests', 'vendor_id')
    op.drop_table('vendors')
