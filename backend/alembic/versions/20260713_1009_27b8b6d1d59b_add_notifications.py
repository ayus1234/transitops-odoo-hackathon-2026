"""add_notifications

Revision ID: 27b8b6d1d59b
Revises: 20261207_add_settings
Create Date: 2026-07-13 10:09:37.160565+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '27b8b6d1d59b'
down_revision = '20261207_add_settings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('notifications',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.Column('priority', sa.String(length=20), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('action_url', sa.String(length=255), nullable=True),
    sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_archived', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("category IN ('Information', 'Success', 'Warning', 'Error')", name='check_notification_category'),
    sa.CheckConstraint("priority IN ('Low', 'Medium', 'High', 'Critical')", name='check_notification_priority'),
    sa.CheckConstraint("type IN ('System', 'Trip', 'Maintenance', 'Fuel', 'Expense', 'Vehicle', 'Driver', 'Report', 'Security', 'Reminder')", name='check_notification_type'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_is_archived'), 'notifications', ['is_archived'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_priority'), 'notifications', ['priority'], unique=False)
    op.create_index(op.f('ix_notifications_type'), 'notifications', ['type'], unique=False)
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_type'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_priority'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_is_archived'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
