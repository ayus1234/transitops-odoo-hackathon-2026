"""Add maintenance model

Revision ID: 20261207_maintenance
Revises: 20261207_trip
Create Date: 2026-12-07 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_maintenance'
down_revision = '20261207_trip'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create maintenance_logs table
    op.create_table(
        'maintenance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('maintenance_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('vehicles.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('maintenance_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='Medium'),
        sa.Column('assigned_technician', sa.String(length=100), nullable=True),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('estimated_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('actual_cost', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('odometer_at_maintenance', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        # Check constraints
        sa.CheckConstraint(
            "status IN ('Pending', 'Approved', 'In Progress', 'Completed', 'Rejected')",
            name='check_maintenance_status'
        ),
        sa.CheckConstraint(
            "priority IN ('Low', 'Medium', 'High', 'Critical')",
            name='check_maintenance_priority'
        ),
        sa.CheckConstraint(
            'estimated_cost >= 0 OR estimated_cost IS NULL',
            name='check_estimated_cost_non_negative'
        ),
        sa.CheckConstraint(
            'actual_cost >= 0 OR actual_cost IS NULL',
            name='check_actual_cost_non_negative'
        ),
    )

    # Create indexes
    op.create_index('ix_maintenance_logs_id', 'maintenance_logs', ['id'])
    op.create_index('ix_maintenance_logs_maintenance_number',
                    'maintenance_logs', ['maintenance_number'])
    op.create_index('ix_maintenance_logs_vehicle_id',
                    'maintenance_logs', ['vehicle_id'])
    op.create_index('ix_maintenance_logs_status',
                    'maintenance_logs', ['status'])
    op.create_index('ix_maintenance_logs_scheduled_date',
                    'maintenance_logs', ['scheduled_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_maintenance_logs_scheduled_date',
                  table_name='maintenance_logs')
    op.drop_index('ix_maintenance_logs_status',
                  table_name='maintenance_logs')
    op.drop_index('ix_maintenance_logs_vehicle_id',
                  table_name='maintenance_logs')
    op.drop_index('ix_maintenance_logs_maintenance_number',
                  table_name='maintenance_logs')
    op.drop_index('ix_maintenance_logs_id',
                  table_name='maintenance_logs')

    # Drop table
    op.drop_table('maintenance_logs')
