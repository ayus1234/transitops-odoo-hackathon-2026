"""Add vehicle model

Revision ID: 20261207_vehicle
Revises: 
Create Date: 2026-12-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_vehicle'
down_revision = '20261206_users_roles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('registration_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('vehicle_name', sa.String(length=100), nullable=False),
        sa.Column('vehicle_type', sa.String(length=50), nullable=False),
        sa.Column('vin', sa.String(length=50), nullable=True),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('variant', sa.String(length=100), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('body_type', sa.String(length=50), nullable=True),
        sa.Column('powertrain', sa.String(length=50), nullable=True),
        sa.Column('capacity_kg', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('seating_capacity', sa.Integer(), nullable=True),
        sa.Column('fuel_type', sa.String(length=50), nullable=False),
        sa.Column('current_odometer_km', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('engine_hours', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0'),
        sa.Column('acquisition_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('acquisition_date', sa.Date(), nullable=True),
        sa.Column('ownership_type', sa.String(length=20), nullable=True),
        sa.Column('lease_provider', sa.String(length=255), nullable=True),
        sa.Column('lease_start_date', sa.Date(), nullable=True),
        sa.Column('lease_end_date', sa.Date(), nullable=True),
        sa.Column('monthly_lease_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('insurance_expiry', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Available'),
        sa.Column('latitude', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('retired_date', sa.Date(), nullable=True),
        sa.Column('sale_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('Ordered', 'Acquired', 'Available', 'Assigned', 'Active', 'On Trip', 'Maintenance', 'In Shop', 'Inactive', 'Retired', 'Sold')", name='check_vehicle_status'),
        sa.CheckConstraint('capacity_kg > 0', name='check_capacity_positive'),
        sa.CheckConstraint('current_odometer_km >= 0', name='check_odometer_non_negative'),
    )
    
    # Create indexes
    op.create_index('ix_vehicles_id', 'vehicles', ['id'])
    op.create_index('ix_vehicles_registration_number', 'vehicles', ['registration_number'])
    op.create_index('ix_vehicles_vehicle_type', 'vehicles', ['vehicle_type'])
    op.create_index('ix_vehicles_status', 'vehicles', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_vehicles_status', table_name='vehicles')
    op.drop_index('ix_vehicles_vehicle_type', table_name='vehicles')
    op.drop_index('ix_vehicles_registration_number', table_name='vehicles')
    op.drop_index('ix_vehicles_id', table_name='vehicles')
    
    # Drop table
    op.drop_table('vehicles')
