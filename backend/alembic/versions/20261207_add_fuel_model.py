"""Add fuel model

Revision ID: 20261207_fuel
Revises: 20261207_maintenance
Create Date: 2026-12-07 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_fuel'
down_revision = '20261207_maintenance'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create fuel_logs table
    op.create_table(
        'fuel_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('vehicles.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True),
        sa.Column('fuel_type', sa.String(length=50), nullable=False),
        sa.Column('quantity_liters', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('cost_per_liter', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('odometer_reading', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('refuel_date', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('station_name', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('receipt_number', sa.String(length=100), nullable=True),
        sa.Column('recorded_by', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        
        # Check constraints
        sa.CheckConstraint(
            'quantity_liters > 0',
            name='check_fuel_quantity_positive'
        ),
        sa.CheckConstraint(
            'cost_per_liter > 0',
            name='check_fuel_cost_per_liter_positive'
        ),
        sa.CheckConstraint(
            'total_cost > 0',
            name='check_fuel_total_cost_positive'
        ),
        sa.CheckConstraint(
            'odometer_reading >= 0',
            name='check_fuel_odometer_non_negative'
        ),
    )

    # Create indexes
    op.create_index('ix_fuel_logs_id', 'fuel_logs', ['id'])
    op.create_index('ix_fuel_logs_vehicle_id', 'fuel_logs', ['vehicle_id'])
    op.create_index('ix_fuel_logs_trip_id', 'fuel_logs', ['trip_id'])
    op.create_index('ix_fuel_logs_refuel_date', 'fuel_logs', ['refuel_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_fuel_logs_refuel_date', table_name='fuel_logs')
    op.drop_index('ix_fuel_logs_trip_id', table_name='fuel_logs')
    op.drop_index('ix_fuel_logs_vehicle_id', table_name='fuel_logs')
    op.drop_index('ix_fuel_logs_id', table_name='fuel_logs')

    # Drop table
    op.drop_table('fuel_logs')
