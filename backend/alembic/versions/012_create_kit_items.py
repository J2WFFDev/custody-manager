"""Create kit_items table

Revision ID: 012_create_kit_items
Revises: 011_next_maintenance
Create Date: 2026-01-28

Implements redesigned kit architecture: represent kits as containers of component items.
Each kit can have multiple items (firearm, optic, case, magazine, tool, etc.) with individual tracking.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '012_create_kit_items'
down_revision: Union[str, None] = '011_next_maintenance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create kit_items table
    op.create_table(
        'kit_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('kit_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(length=50), nullable=False),
        sa.Column('make', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number_encrypted', sa.String(length=500), nullable=True),
        sa.Column('friendly_name', sa.String(length=200), nullable=True),
        sa.Column('photo_url', sa.String(length=500), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('status', sa.Enum('in_kit', 'checked_out', 'lost', 'maintenance', name='kititemstatus'), nullable=False, server_default='in_kit'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index(op.f('ix_kit_items_id'), 'kit_items', ['id'], unique=False)
    op.create_index(op.f('ix_kit_items_kit_id'), 'kit_items', ['kit_id'], unique=False)
    op.create_index(op.f('ix_kit_items_item_type'), 'kit_items', ['item_type'], unique=False)


def downgrade() -> None:
    # Drop indexes and table
    op.drop_index(op.f('ix_kit_items_item_type'), table_name='kit_items')
    op.drop_index(op.f('ix_kit_items_kit_id'), table_name='kit_items')
    op.drop_index(op.f('ix_kit_items_id'), table_name='kit_items')
    op.drop_table('kit_items')
    op.execute('DROP TYPE kititemstatus')
