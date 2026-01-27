"""add encrypted serial number to kits

Revision ID: 008_add_encrypted_serial_number
Revises: 007_convert_user_role_to_enum
Create Date: 2026-01-27

Implements AUDIT-003: Field-level encryption for serial numbers
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_encrypted_serial_number'
down_revision = '007_convert_user_role_to_enum'
branch_labels = None
depends_on = None


def upgrade():
    # Add encrypted serial number column to kits table
    op.add_column('kits', 
        sa.Column('serial_number_encrypted', sa.String(length=500), nullable=True)
    )


def downgrade():
    # Remove encrypted serial number column
    op.drop_column('kits', 'serial_number_encrypted')
