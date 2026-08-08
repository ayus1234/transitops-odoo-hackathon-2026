"""add vehicle_telemetry_logs table

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-08-08 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h8i9j0k1l2m3'
down_revision = 'g7h8i9j0k1l2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vehicle_telemetry_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('altitude_m', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('speed_kmh', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('heading', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('accuracy_m', sa.Float(), nullable=True, server_default='5.0'),
        sa.Column('ignition', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fuel_level_percent', sa.Float(), nullable=True),
        sa.Column('engine_temp_c', sa.Float(), nullable=True),
        sa.Column('battery_voltage', sa.Float(), nullable=True),
        sa.Column('odometer_km', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('engine_rpm', sa.Float(), nullable=True),
        sa.Column('diagnostics', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    op.create_index('ix_vehicle_telemetry_logs_vehicle_id', 'vehicle_telemetry_logs', ['vehicle_id'])
    op.create_index('ix_vehicle_telemetry_logs_trip_id', 'vehicle_telemetry_logs', ['trip_id'])
    op.create_index('ix_vehicle_telemetry_logs_timestamp', 'vehicle_telemetry_logs', ['timestamp'])
    op.create_index('ix_telemetry_vehicle_timestamp', 'vehicle_telemetry_logs', ['vehicle_id', 'timestamp'])
    op.create_index('ix_telemetry_trip_timestamp', 'vehicle_telemetry_logs', ['trip_id', 'timestamp'])


def downgrade():
    op.drop_table('vehicle_telemetry_logs')
