"""Create maintenance_events table

Revision ID: 006_create_maintenance_events
Revises: 005
Create Date: 2026-01-27

Implements MAINT-001: Track equipment maintenance events
"""
from typing import Sequence, Union

"""create maintenance events table

Revision ID: 006_create_maintenance_events
Revises: 005_add_attestation_fields
Create Date: 2026-01-27 01:58:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_create_maintenance_events'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create maintenance_events table
    op.create_table(
        'maintenance_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        # Event type enum
        sa.Column('event_type', sa.Enum('open', 'close', 'parts_replacement', 'inspection', 'cleaning', name='maintenanceeventtype'), nullable=False),
        # Kit reference
        sa.Column('kit_id', sa.Integer(), nullable=False),
        # Who performed the maintenance
        sa.Column('performed_by_id', sa.Integer(), nullable=False),
        sa.Column('performed_by_name', sa.String(length=200), nullable=False),
        # Maintenance details
        sa.Column('round_count', sa.Integer(), nullable=True),
        sa.Column('parts_replaced', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('next_maintenance_date', sa.Date(), nullable=True),
        # Constraints
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['performed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes
    op.create_index(op.f('ix_maintenance_events_id'), 'maintenance_events', ['id'], unique=False)
revision = '006_create_maintenance_events'
down_revision = '005_add_attestation_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'maintenance_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kit_id', sa.Integer(), nullable=False),
        sa.Column('opened_by_id', sa.Integer(), nullable=False),
        sa.Column('opened_by_name', sa.String(length=200), nullable=False),
        sa.Column('closed_by_id', sa.Integer(), nullable=True),
        sa.Column('closed_by_name', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('parts_replaced', sa.Text(), nullable=True),
        sa.Column('round_count', sa.Integer(), nullable=True),
        sa.Column('is_open', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['opened_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_maintenance_events_kit_id'), 'maintenance_events', ['kit_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and table
    op.drop_index(op.f('ix_maintenance_events_kit_id'), table_name='maintenance_events')
    op.drop_index(op.f('ix_maintenance_events_id'), table_name='maintenance_events')
    op.drop_table('maintenance_events')
    op.execute('DROP TYPE maintenanceeventtype')
    op.drop_index(op.f('ix_maintenance_events_kit_id'), table_name='maintenance_events')
    op.drop_table('maintenance_events')
