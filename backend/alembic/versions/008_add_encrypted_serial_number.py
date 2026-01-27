"""Add encrypted serial_number column to kits

Revision ID: 008_add_encrypted_serial_number
Revises: 007_convert_user_role_to_enum
Create Date: 2026-01-27 17:00:00.000000

"""
from typing import Sequence, Union

"""add encrypted serial number to kits

Revision ID: 008_add_encrypted_serial_number
Revises: 007_convert_user_role_to_enum
Create Date: 2026-01-27

Implements AUDIT-003: Field-level encryption for serial numbers
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_add_encrypted_serial_number'
down_revision: Union[str, None] = '007_convert_user_role_to_enum'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add encrypted serial_number column to kits table.
    
    This implements AUDIT-003: Serial numbers are encrypted in the database
    to protect them from data breaches. The encryption is handled automatically
    by the EncryptedString SQLAlchemy type.
    """
    # Add serial_number column with sufficient length for encrypted data
    # Encrypted data is larger than plaintext, so we use 500 chars to handle
    # encryption overhead for a 50-char serial number
    op.add_column('kits', sa.Column('serial_number', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove serial_number column from kits table."""
    op.drop_column('kits', 'serial_number')
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
