"""add audit_events table

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-08-08 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g7h8i9j0k1l2'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('driver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('drivers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )

    op.create_index('ix_audit_events_event_type', 'audit_events', ['event_type'])
    op.create_index('ix_audit_events_entity_type', 'audit_events', ['entity_type'])
    op.create_index('ix_audit_events_entity_id', 'audit_events', ['entity_id'])
    op.create_index('ix_audit_events_job_id', 'audit_events', ['job_id'])
    op.create_index('ix_audit_events_trip_id', 'audit_events', ['trip_id'])
    op.create_index('ix_audit_events_vehicle_id', 'audit_events', ['vehicle_id'])
    op.create_index('ix_audit_events_driver_id', 'audit_events', ['driver_id'])
    op.create_index('ix_audit_events_created_at', 'audit_events', ['created_at'])
    op.create_index('ix_audit_events_job_timeline', 'audit_events', ['job_id', 'created_at'])
    op.create_index('ix_audit_events_trip_timeline', 'audit_events', ['trip_id', 'created_at'])


def downgrade():
    op.drop_table('audit_events')
