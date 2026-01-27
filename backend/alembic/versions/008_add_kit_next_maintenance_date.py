"""add next_maintenance_date to kits

Revision ID: 008_add_kit_next_maintenance_date
Revises: 007_convert_user_role_to_enum
Create Date: 2026-01-27

Implements MAINT-002: Track next maintenance due date for kits
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_kit_next_maintenance_date'
down_revision = '007_convert_user_role_to_enum'
branch_labels = None
depends_on = None


def upgrade():
    # Add next_maintenance_date column to kits table
    op.add_column('kits', sa.Column('next_maintenance_date', sa.Date(), nullable=True))


def downgrade():
    # Remove next_maintenance_date column from kits table
    op.drop_column('kits', 'next_maintenance_date')
