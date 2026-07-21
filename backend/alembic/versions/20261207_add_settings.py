"""add settings and permissions tables

Revision ID: 20261207_add_settings
Revises: 20261207_add_expense_model
Create Date: 2026-12-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_add_settings'
down_revision = '20261207_expense'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === permissions table ===
    op.create_table(
        'permissions',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('resource', sa.String(50), nullable=False, index=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # === application_settings table ===
    op.create_table(
        'application_settings',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('key', sa.String(50), nullable=False, unique=True),
        sa.Column('app_name', sa.String(100), nullable=False, server_default='TransitOps ERP'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('date_format', sa.String(20), nullable=False, server_default='YYYY-MM-DD'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='INR'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('maintenance_alert_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('license_expiry_alert_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('max_trip_duration_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('auto_approve_expenses_below', sa.Float(), nullable=False, server_default='0'),
        sa.Column('features', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # === organization_settings table ===
    op.create_table(
        'organization_settings',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('key', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False, server_default='TransitOps Inc.'),
        sa.Column('legal_name', sa.String(200), nullable=True),
        sa.Column('email', sa.String(255), nullable=False, server_default='admin@transitops.com'),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('address_line1', sa.String(255), nullable=True),
        sa.Column('address_line2', sa.String(255), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True, server_default='India'),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('registration_number', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('organization_settings')
    op.drop_table('application_settings')
    op.drop_table('permissions')
