"""Add encrypted serial_number column to kits

Revision ID: 008_encrypted_serial
Revises: 007_convert_user_role_to_enum
Create Date: 2026-01-27 17:00:00.000000

Implements AUDIT-003: Field-level encryption for serial numbers
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_encrypted_serial'
down_revision: Union[str, None] = '007_convert_user_role_to_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add encrypted serial_number column to kits table."""
    op.add_column('kits', sa.Column('serial_number', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove serial_number column from kits table."""
    op.drop_column('kits', 'serial_number')
