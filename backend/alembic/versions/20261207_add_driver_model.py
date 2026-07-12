"""Add driver model

Revision ID: 20261207_driver
Revises: 20261207_vehicle
Create Date: 2026-12-07 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_driver'
down_revision = '20261207_vehicle'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create drivers table
    op.create_table(
        'drivers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('license_number', sa.String(length=50), nullable=False, unique=True),
        sa.Column('license_category', sa.String(length=50), nullable=False),
        sa.Column('license_issue_date', sa.Date(), nullable=False),
        sa.Column('license_expiry_date', sa.Date(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('emergency_contact', sa.String(length=20), nullable=True),
        sa.Column('safety_score', sa.Numeric(precision=5, scale=2), nullable=False, server_default='100.00'),
        sa.Column('total_trips', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Available'),
        sa.Column('joined_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('Available', 'On Trip', 'Off Duty', 'Suspended')", name='check_driver_status'),
        sa.CheckConstraint('safety_score >= 0 AND safety_score <= 100', name='check_safety_score_range'),
        sa.CheckConstraint('total_trips >= 0', name='check_total_trips_non_negative'),
        sa.CheckConstraint('license_expiry_date > license_issue_date', name='check_license_dates'),
    )
    
    # Create indexes
    op.create_index('ix_drivers_id', 'drivers', ['id'])
    op.create_index('ix_drivers_user_id', 'drivers', ['user_id'])
    op.create_index('ix_drivers_license_number', 'drivers', ['license_number'])
    op.create_index('ix_drivers_status', 'drivers', ['status'])
    op.create_index('ix_drivers_license_expiry_date', 'drivers', ['license_expiry_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_drivers_license_expiry_date', table_name='drivers')
    op.drop_index('ix_drivers_status', table_name='drivers')
    op.drop_index('ix_drivers_license_number', table_name='drivers')
    op.drop_index('ix_drivers_user_id', table_name='drivers')
    op.drop_index('ix_drivers_id', table_name='drivers')
    
    # Drop table
    op.drop_table('drivers')
