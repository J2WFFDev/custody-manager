"""create maintenance events table

Revision ID: 006_create_maintenance_events
Revises: 005_add_attestation_fields
Create Date: 2026-01-27 01:58:00.000000

Implements MAINT-001: Track equipment maintenance events
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_create_maintenance_events'
down_revision: Union[str, None] = '005_add_attestation_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'maintenance_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('kit_id', sa.Integer(), nullable=False),
        sa.Column('opened_by_id', sa.Integer(), nullable=False),
        sa.Column('opened_by_name', sa.String(length=200), nullable=False),
        sa.Column('closed_by_id', sa.Integer(), nullable=True),
        sa.Column('closed_by_name', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('parts_replaced', sa.Text(), nullable=True),
        sa.Column('round_count', sa.Integer(), nullable=True),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['opened_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_maintenance_events_id'), 'maintenance_events', ['id'], unique=False)
    op.create_index(op.f('ix_maintenance_events_kit_id'), 'maintenance_events', ['kit_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_maintenance_events_kit_id'), table_name='maintenance_events')
    op.drop_index(op.f('ix_maintenance_events_id'), table_name='maintenance_events')
    op.drop_table('maintenance_events')
