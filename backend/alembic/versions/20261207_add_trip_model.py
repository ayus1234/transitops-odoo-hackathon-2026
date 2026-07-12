"""Add trip model

Revision ID: 20261207_trip
Revises: 20261207_driver
Create Date: 2026-12-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_trip'
down_revision = '20261207_driver'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create trips table
    op.create_table(
        'trips',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('trip_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=False),
        sa.Column('cargo_weight_kg', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('planned_distance_km', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('actual_distance_km', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('planned_departure', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_departure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('planned_arrival', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('start_odometer_km', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('end_odometer_km', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('fuel_consumed_liters', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Draft'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("status IN ('Draft', 'Dispatched', 'Completed', 'Cancelled')", name='check_trip_status'),
        sa.CheckConstraint('cargo_weight_kg > 0', name='check_cargo_weight_positive'),
        sa.CheckConstraint('planned_distance_km > 0', name='check_planned_distance_positive'),
        sa.CheckConstraint('actual_distance_km >= 0 OR actual_distance_km IS NULL', name='check_actual_distance_non_negative'),
        sa.CheckConstraint('end_odometer_km >= start_odometer_km OR end_odometer_km IS NULL', name='check_odometer_order'),
    )
    
    # Create indexes
    op.create_index('ix_trips_id', 'trips', ['id'])
    op.create_index('ix_trips_trip_number', 'trips', ['trip_number'])
    op.create_index('ix_trips_vehicle_id', 'trips', ['vehicle_id'])
    op.create_index('ix_trips_driver_id', 'trips', ['driver_id'])
    op.create_index('ix_trips_status', 'trips', ['status'])
    op.create_index('ix_trips_planned_departure', 'trips', ['planned_departure'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_trips_planned_departure', table_name='trips')
    op.drop_index('ix_trips_status', table_name='trips')
    op.drop_index('ix_trips_driver_id', table_name='trips')
    op.drop_index('ix_trips_vehicle_id', table_name='trips')
    op.drop_index('ix_trips_trip_number', table_name='trips')
    op.drop_index('ix_trips_id', table_name='trips')
    
    # Drop table
    op.drop_table('trips')
