"""Add jobs and trip_stops tables for transportation management

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-01 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create jobs table
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_contact', sa.String(length=255), nullable=True),
        sa.Column('pickup_address', sa.Text(), nullable=False),
        sa.Column('delivery_address', sa.Text(), nullable=False),
        sa.Column('pickup_latitude', sa.Float(), nullable=True),
        sa.Column('pickup_longitude', sa.Float(), nullable=True),
        sa.Column('delivery_latitude', sa.Float(), nullable=True),
        sa.Column('delivery_longitude', sa.Float(), nullable=True),
        sa.Column('cargo_description', sa.Text(), nullable=True),
        sa.Column('cargo_weight_kg', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cargo_volume_cbm', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='Normal'),
        sa.Column('time_window_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_window_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.create_index('ix_jobs_job_number', 'jobs', ['job_number'])
    op.create_index('ix_jobs_customer_name', 'jobs', ['customer_name'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_jobs_priority', 'jobs', ['priority'])

    # 2. Create trip_stops table
    op.create_table(
        'trip_stops',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False, default=1),
        sa.Column('location_name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('stop_type', sa.String(length=30), nullable=False, server_default='Waypoint'),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('planned_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('planned_departure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_arrival', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_departure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('proof_of_delivery', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    op.create_index('ix_trip_stops_trip_id', 'trip_stops', ['trip_id'])
    op.create_index('ix_trip_stops_job_id', 'trip_stops', ['job_id'])


def downgrade():
    op.drop_index('ix_trip_stops_job_id', table_name='trip_stops')
    op.drop_index('ix_trip_stops_trip_id', table_name='trip_stops')
    op.drop_table('trip_stops')

    op.drop_index('ix_jobs_priority', table_name='jobs')
    op.drop_index('ix_jobs_status', table_name='jobs')
    op.drop_index('ix_jobs_customer_name', table_name='jobs')
    op.drop_index('ix_jobs_job_number', table_name='jobs')
    op.drop_table('jobs')
