"""Create kits table

Revision ID: 001_create_kits
Revises: 
Create Date: 2026-01-26 23:19:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_create_kits'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create kits table
    op.create_table(
        'kits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('qr_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('serial_number', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('qr_code')
    )
    op.create_index(op.f('ix_kits_id'), 'kits', ['id'], unique=False)
    op.create_index(op.f('ix_kits_qr_code'), 'kits', ['qr_code'], unique=True)


def downgrade() -> None:
    # Drop kits table
    op.drop_index(op.f('ix_kits_qr_code'), table_name='kits')
    op.drop_index(op.f('ix_kits_id'), table_name='kits')
    op.drop_table('kits')
