"""Add Driver 360 columns

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-07-28 18:14:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('drivers', sa.Column('license_class', sa.String(50), nullable=True))
    op.add_column('drivers', sa.Column('blood_group', sa.String(10), nullable=True))
    op.add_column('drivers', sa.Column('medical_fitness_expiry', sa.Date(), nullable=True))
    op.add_column('drivers', sa.Column('efficiency_score', sa.Numeric(5, 2), nullable=True, server_default='100.00'))
    op.add_column('drivers', sa.Column('compliance_score', sa.Numeric(5, 2), nullable=True, server_default='100.00'))
    op.add_column('drivers', sa.Column('overall_score', sa.Numeric(5, 2), nullable=True, server_default='100.00'))
    op.add_column('drivers', sa.Column('current_vehicle_id', sa.Uuid(as_uuid=True),
                  sa.ForeignKey('vehicles.id', ondelete='SET NULL'), nullable=True, index=True))
    op.add_column('drivers', sa.Column('latitude', sa.Numeric(10, 6), nullable=True))
    op.add_column('drivers', sa.Column('longitude', sa.Numeric(10, 6), nullable=True))
    op.add_column('drivers', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('drivers', 'notes')
    op.drop_column('drivers', 'current_vehicle_id')
    op.drop_column('drivers', 'overall_score')
    op.drop_column('drivers', 'compliance_score')
    op.drop_column('drivers', 'efficiency_score')
    op.drop_column('drivers', 'medical_fitness_expiry')
    op.drop_column('drivers', 'blood_group')
    op.drop_column('drivers', 'license_class')
