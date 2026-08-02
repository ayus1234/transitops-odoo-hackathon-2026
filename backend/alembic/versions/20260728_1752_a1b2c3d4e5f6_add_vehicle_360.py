"""Add Vehicle 360 columns and expand lifecycle states

Revision ID: a1b2c3d4e5f6
Revises: 20260716_0100_5ce577173c60
Create Date: 2026-07-28 17:52:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5ce577173c60'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Add new Vehicle 360 columns (all nullable for backward compat) ---
    op.add_column('vehicles', sa.Column('vin', sa.String(50), nullable=True))
    op.add_column('vehicles', sa.Column('variant', sa.String(100), nullable=True))
    op.add_column('vehicles', sa.Column('body_type', sa.String(50), nullable=True))
    op.add_column('vehicles', sa.Column('powertrain', sa.String(50), nullable=True))
    op.add_column('vehicles', sa.Column('seating_capacity', sa.Integer(), nullable=True))
    op.add_column('vehicles', sa.Column('ownership_type', sa.String(20), nullable=True))
    op.add_column('vehicles', sa.Column('lease_provider', sa.String(255), nullable=True))
    op.add_column('vehicles', sa.Column('lease_start_date', sa.Date(), nullable=True))
    op.add_column('vehicles', sa.Column('lease_end_date', sa.Date(), nullable=True))
    op.add_column('vehicles', sa.Column('monthly_lease_cost', sa.Numeric(12, 2), nullable=True))
    op.add_column('vehicles', sa.Column('engine_hours', sa.Numeric(10, 2), nullable=True, server_default='0'))
    op.add_column('vehicles', sa.Column('retired_date', sa.Date(), nullable=True))
    op.add_column('vehicles', sa.Column('sale_price', sa.Numeric(12, 2), nullable=True))
    op.add_column('vehicles', sa.Column('notes', sa.Text(), nullable=True))

    # Create unique index on VIN (partial — only non-null values)
    op.create_index('ix_vehicles_vin', 'vehicles', ['vin'], unique=True,
                    postgresql_where=sa.text('vin IS NOT NULL'))

    # --- Expand vehicle status CHECK constraint ---
    # Drop old constraint and create expanded one
    op.drop_constraint('check_vehicle_status', 'vehicles', type_='check')
    op.create_check_constraint(
        'check_vehicle_status',
        'vehicles',
        "status IN ('Ordered', 'Acquired', 'Available', 'Assigned', 'Active', "
        "'On Trip', 'Maintenance', 'In Shop', 'Inactive', 'Retired', 'Sold')"
    )


def downgrade() -> None:
    # Revert status constraint to original
    op.drop_constraint('check_vehicle_status', 'vehicles', type_='check')
    op.create_check_constraint(
        'check_vehicle_status',
        'vehicles',
        "status IN ('Available', 'On Trip', 'In Shop', 'Retired')"
    )

    # Drop VIN index
    op.drop_index('ix_vehicles_vin', 'vehicles')

    # Drop new columns
    op.drop_column('vehicles', 'notes')
    op.drop_column('vehicles', 'sale_price')
    op.drop_column('vehicles', 'retired_date')
    op.drop_column('vehicles', 'engine_hours')
    op.drop_column('vehicles', 'monthly_lease_cost')
    op.drop_column('vehicles', 'lease_end_date')
    op.drop_column('vehicles', 'lease_start_date')
    op.drop_column('vehicles', 'lease_provider')
    op.drop_column('vehicles', 'ownership_type')
    op.drop_column('vehicles', 'seating_capacity')
    op.drop_column('vehicles', 'powertrain')
    op.drop_column('vehicles', 'body_type')
    op.drop_column('vehicles', 'variant')
    op.drop_column('vehicles', 'vin')
