"""Add expense model

Revision ID: 20261207_expense
Revises: 20261207_fuel
Create Date: 2026-12-07 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261207_expense'
down_revision = '20261207_fuel'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create expenses table
    op.create_table(
        'expenses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('expense_type', sa.String(length=50), nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('vehicles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('trip_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True),
        sa.Column('maintenance_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('maintenance_logs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('receipt_number', sa.String(length=100), nullable=True),
        sa.Column('vendor_name', sa.String(length=255), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('recorded_by', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        
        # Check constraints
        sa.CheckConstraint(
            "expense_type IN ('Fuel', 'Maintenance', 'Toll', 'Repair', 'Miscellaneous')",
            name='check_expense_type'
        ),
        sa.CheckConstraint(
            "status IN ('Pending', 'Approved', 'Rejected')",
            name='check_expense_status'
        ),
        sa.CheckConstraint(
            'amount > 0',
            name='check_expense_amount_positive'
        ),
    )

    # Create indexes
    op.create_index('ix_expenses_id', 'expenses', ['id'])
    op.create_index('ix_expenses_expense_type', 'expenses', ['expense_type'])
    op.create_index('ix_expenses_vehicle_id', 'expenses', ['vehicle_id'])
    op.create_index('ix_expenses_trip_id', 'expenses', ['trip_id'])
    op.create_index('ix_expenses_maintenance_id', 'expenses', ['maintenance_id'])
    op.create_index('ix_expenses_expense_date', 'expenses', ['expense_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_expenses_expense_date', table_name='expenses')
    op.drop_index('ix_expenses_maintenance_id', table_name='expenses')
    op.drop_index('ix_expenses_trip_id', table_name='expenses')
    op.drop_index('ix_expenses_vehicle_id', table_name='expenses')
    op.drop_index('ix_expenses_expense_type', table_name='expenses')
    op.drop_index('ix_expenses_id', table_name='expenses')

    # Drop table
    op.drop_table('expenses')
