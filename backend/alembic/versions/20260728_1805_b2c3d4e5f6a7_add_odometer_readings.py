"""Add odometer_readings table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-28 18:05:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'odometer_readings',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('vehicle_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('vehicles.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('reading_km', sa.Numeric(10, 2), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(20), nullable=False, server_default='manual'),
        sa.Column('recorded_by', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('trip_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('trips.id', ondelete='SET NULL'),
                  nullable=True, index=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )

    # Composite index for efficient per-vehicle chronological queries
    op.create_index(
        'ix_odometer_vehicle_recorded',
        'odometer_readings',
        ['vehicle_id', 'recorded_at']
    )


def downgrade() -> None:
    op.drop_index('ix_odometer_vehicle_recorded', 'odometer_readings')
    op.drop_table('odometer_readings')
