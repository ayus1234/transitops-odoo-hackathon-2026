"""add_timeline_to_maintenance

Revision ID: 5ce577173c60
Revises: 4bd466062b59
Create Date: 2026-07-16 01:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ce577173c60'
down_revision = '6aa05cc0d08c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table('maintenance_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('end_time', sa.Time(), nullable=True))
        batch_op.add_column(sa.Column('estimated_duration', sa.Integer(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('maintenance_logs', schema=None) as batch_op:
        batch_op.drop_column('estimated_duration')
        batch_op.drop_column('end_time')
        batch_op.drop_column('start_time')
