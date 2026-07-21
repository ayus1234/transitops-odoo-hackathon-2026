"""enhance_support_tickets

Revision ID: 4bd466062b59
Revises: ae049a58d200
Create Date: 2026-07-15 18:09:28.417356+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bd466062b59'
down_revision = 'ae049a58d200'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('support_tickets', schema=None) as batch_op:
        pass
        # batch_op.add_column(sa.Column('title', sa.String(length=100), nullable=True))
        # batch_op.add_column(sa.Column('type', sa.String(length=50), nullable=True))
        # batch_op.add_column(sa.Column('module_name', sa.String(length=50), nullable=True))
        # batch_op.add_column(sa.Column('created_by', sa.UUID(), nullable=True))
        # batch_op.add_column(sa.Column('resolution_notes', sa.Text(), nullable=True))
        # batch_op.add_column(sa.Column('attachment_url', sa.String(length=255), nullable=True))
        # batch_op.add_column(sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True))

        # Drop old columns (requires named foreign key for user_id in postgres, but sqlite is relaxed)
        # Note: In a true prod env, we'd copy data from subject->title, user_id->created_by, etc.
        # batch_op.drop_column('subject')
        # batch_op.drop_column('resolution')
        # batch_op.drop_column('attachments')
        
    # We must execute raw SQL for data copy if needed, but since we are seeding anew, 
    # we'll just fix the nullables.
    with op.batch_alter_table('support_tickets', schema=None) as batch_op:
        batch_op.alter_column('title', existing_type=sa.String(length=200), nullable=False)
        batch_op.alter_column('module_name', existing_type=sa.String(length=50), nullable=False)
        
        # Recreate FK
        # Note: dropping user_id might fail on SQLite if foreign keys are enforced, 
        # but Alembic batch alter table recreates the table.
        # We will keep user_id for now and just add created_by to avoid SQLite constraint dropping issues, 
        # or we just let batch_op do it.
        # It's safer to just let the seeder drop all tables and recreate.
