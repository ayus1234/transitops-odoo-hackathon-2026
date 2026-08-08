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
    # 0. Create inventory tables
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('part_number', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantity_available', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_reserved', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('minimum_stock_level', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('critical_stock_level', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('unit_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('vendor', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='In Stock'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'procurement_requests',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('procurement_id', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('part_id', sa.Uuid(as_uuid=True), sa.ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requested_by_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_by_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('required_quantity', sa.Integer(), nullable=False),
        sa.Column('suggested_quantity', sa.Integer(), nullable=True),
        sa.Column('vendor', sa.String(255), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('priority', sa.String(50), nullable=False, server_default='Medium'),
        sa.Column('status', sa.String(50), nullable=False, server_default='Draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('po_number', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('procurement_request_id', sa.Uuid(as_uuid=True), sa.ForeignKey('procurement_requests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('cost', sa.Float(), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tracking_id', sa.String(100), nullable=True),
        sa.Column('shipment_status', sa.String(50), nullable=False, server_default='Processing'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'inventory_history',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('part_id', sa.Uuid(as_uuid=True), sa.ForeignKey('inventory_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('quantity_changed', sa.Integer(), nullable=False),
        sa.Column('previous_quantity', sa.Integer(), nullable=False),
        sa.Column('new_quantity', sa.Integer(), nullable=False),
        sa.Column('vendor', sa.String(255), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('user_id', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reference_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

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
    op.drop_table('inventory_history')
    op.drop_table('purchase_orders')
    op.drop_table('procurement_requests')
    op.drop_table('inventory_items')
