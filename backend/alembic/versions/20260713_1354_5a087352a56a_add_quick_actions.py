"""add_quick_actions

Revision ID: 5a087352a56a
Revises: 0d0ab55c0d72
Create Date: 2026-07-13 13:54:03.787299+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a087352a56a'
down_revision = '0d0ab55c0d72'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create quick_actions table
    op.create_table(
        'quick_actions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('route', sa.String(length=255), nullable=False),
        sa.Column('permission_resource', sa.String(length=50), nullable=False),
        sa.Column('permission_action', sa.String(length=50), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_quick_actions_id'), 'quick_actions', ['id'], unique=False)
    op.create_index(op.f('ix_quick_actions_category'), 'quick_actions', ['category'], unique=False)

    # Create user_favorite_actions table
    op.create_table(
        'user_favorite_actions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('action_id', sa.Uuid(), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['action_id'], ['quick_actions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'action_id', name='uq_user_favorite_action')
    )
    op.create_index(op.f('ix_user_favorite_actions_id'), 'user_favorite_actions', ['id'], unique=False)
    op.create_index(op.f('ix_user_favorite_actions_user_id'), 'user_favorite_actions', ['user_id'], unique=False)

    # Create user_recent_actions table
    op.create_table(
        'user_recent_actions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('action_id', sa.Uuid(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['action_id'], ['quick_actions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'action_id', name='uq_user_recent_action')
    )
    op.create_index(op.f('ix_user_recent_actions_id'), 'user_recent_actions', ['id'], unique=False)
    op.create_index(op.f('ix_user_recent_actions_user_id'), 'user_recent_actions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_recent_actions_last_accessed_at'), 'user_recent_actions', ['last_accessed_at'], unique=False)


def downgrade() -> None:
    op.drop_table('user_recent_actions')
    op.drop_table('user_favorite_actions')
    op.drop_table('quick_actions')
