"""add custom reports

Revision ID: b933fe5721cc
Revises: 5a087352a56a
Create Date: 2026-07-13 15:42:19.460873+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b933fe5721cc'
down_revision = '5a087352a56a'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('custom_reports',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('module', sa.String(), nullable=False),
    sa.Column('selected_fields', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=False),
    sa.Column('filters', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('group_by', sa.String(), nullable=True),
    sa.Column('sort_by', sa.String(), nullable=True),
    sa.Column('sort_order', sa.String(), nullable=True),
    sa.Column('chart_type', sa.String(), nullable=True),
    sa.Column('export_formats', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=True),
    sa.Column('created_by', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('report_executions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('report_id', sa.UUID(), nullable=False),
    sa.Column('executed_by', sa.UUID(), nullable=True),
    sa.Column('execution_time', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('duration_ms', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('row_count', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['executed_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['report_id'], ['custom_reports.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('scheduled_reports',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('report_id', sa.UUID(), nullable=False),
    sa.Column('frequency', sa.String(), nullable=False),
    sa.Column('cron_expression', sa.String(), nullable=True),
    sa.Column('next_run', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
    sa.Column('email_recipients', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['report_id'], ['custom_reports.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('scheduled_reports')
    op.drop_table('report_executions')
    op.drop_table('custom_reports')
