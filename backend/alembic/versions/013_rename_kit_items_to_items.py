"""Rename kit_items to items and add item-first architecture support

Revision ID: 013_rename_kit_items_to_items
Revises: 012_create_kit_items
Create Date: 2026-01-28

This migration transforms the system from kit-first to item-first architecture:
- Renames kit_items table to items (master inventory)
- Renames kit_id to current_kit_id (nullable - items can be unassigned)
- Updates status enum to support new item statuses (available, assigned, etc.)
- Existing items remain assigned to their kits (backward compatible)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '013_rename_kit_items_to_items'
down_revision: Union[str, None] = '012_create_kit_items'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Rename table from kit_items to items
    op.rename_table('kit_items', 'items')
    
    # Step 2: Drop old indexes (they reference the old table name)
    op.drop_index('ix_kit_items_item_type', table_name='items')
    op.drop_index('ix_kit_items_kit_id', table_name='items')
    op.drop_index('ix_kit_items_id', table_name='items')
    
    # Step 3: Create new ItemStatus enum with additional statuses
    # First create the new enum type
    op.execute("""
        CREATE TYPE itemstatus AS ENUM (
            'available', 'assigned', 'checked_out', 'lost', 'maintenance'
        )
    """)
    
    # Step 4: Add new status column (temporarily nullable)
    op.add_column('items', sa.Column('status_new', sa.Enum('available', 'assigned', 'checked_out', 'lost', 'maintenance', name='itemstatus'), nullable=True))
    
    # Step 5: Migrate existing status values to new enum
    # Map old KitItemStatus values to new ItemStatus values
    op.execute("""
        UPDATE items SET status_new = CASE
            WHEN status = 'in_kit' THEN 'assigned'::itemstatus
            WHEN status = 'checked_out' THEN 'checked_out'::itemstatus
            WHEN status = 'lost' THEN 'lost'::itemstatus
            WHEN status = 'maintenance' THEN 'maintenance'::itemstatus
            ELSE 'assigned'::itemstatus
        END
    """)
    
    # Step 6: Drop old status column and rename new one
    op.drop_column('items', 'status')
    op.alter_column('items', 'status_new', new_column_name='status', nullable=False)
    
    # Step 7: Rename kit_id to current_kit_id and make it nullable
    op.alter_column('items', 'kit_id',
                    new_column_name='current_kit_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # Step 8: Update foreign key constraint
    # Drop old FK constraint
    op.drop_constraint('kit_items_kit_id_fkey', 'items', type_='foreignkey')
    # Create new FK constraint with ON DELETE SET NULL (items can exist without kits)
    op.create_foreign_key(
        'items_current_kit_id_fkey',
        'items', 'kits',
        ['current_kit_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Step 9: Create new indexes
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_current_kit_id'), 'items', ['current_kit_id'], unique=False)
    op.create_index(op.f('ix_items_item_type'), 'items', ['item_type'], unique=False)
    op.create_index(op.f('ix_items_status'), 'items', ['status'], unique=False)
    
    # Step 10: Drop old enum type
    op.execute('DROP TYPE kititemstatus')


def downgrade() -> None:
    # Reverse the migration
    
    # Step 1: Drop new indexes
    op.drop_index(op.f('ix_items_status'), table_name='items')
    op.drop_index(op.f('ix_items_item_type'), table_name='items')
    op.drop_index(op.f('ix_items_current_kit_id'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    
    # Step 2: Recreate old KitItemStatus enum
    op.execute("""
        CREATE TYPE kititemstatus AS ENUM (
            'in_kit', 'checked_out', 'lost', 'maintenance'
        )
    """)
    
    # Step 3: Add temporary column with old enum
    op.add_column('items', sa.Column('status_old', sa.Enum('in_kit', 'checked_out', 'lost', 'maintenance', name='kititemstatus'), nullable=True))
    
    # Step 4: Migrate status values back
    op.execute("""
        UPDATE items SET status_old = CASE
            WHEN status IN ('available', 'assigned') THEN 'in_kit'::kititemstatus
            WHEN status = 'checked_out' THEN 'checked_out'::kititemstatus
            WHEN status = 'lost' THEN 'lost'::kititemstatus
            WHEN status = 'maintenance' THEN 'maintenance'::kititemstatus
            ELSE 'in_kit'::kititemstatus
        END
    """)
    
    # Step 5: Drop new status column and rename old one
    op.drop_column('items', 'status')
    op.alter_column('items', 'status_old', new_column_name='status', nullable=False)
    
    # Step 6: Rename current_kit_id back to kit_id and make it non-nullable
    # Note: This will fail if there are items with NULL current_kit_id
    op.alter_column('items', 'current_kit_id',
                    new_column_name='kit_id',
                    existing_type=sa.Integer(),
                    nullable=False)
    
    # Step 7: Update foreign key constraint back
    op.drop_constraint('items_current_kit_id_fkey', 'items', type_='foreignkey')
    op.create_foreign_key(
        'kit_items_kit_id_fkey',
        'items', 'kits',
        ['kit_id'], ['id']
    )
    
    # Step 8: Rename table back
    op.rename_table('items', 'kit_items')
    
    # Step 9: Create old indexes
    op.create_index(op.f('ix_kit_items_item_type'), 'kit_items', ['item_type'], unique=False)
    op.create_index(op.f('ix_kit_items_kit_id'), 'kit_items', ['kit_id'], unique=False)
    op.create_index(op.f('ix_kit_items_id'), 'kit_items', ['id'], unique=False)
    
    # Step 10: Drop new enum type
    op.execute('DROP TYPE itemstatus')
