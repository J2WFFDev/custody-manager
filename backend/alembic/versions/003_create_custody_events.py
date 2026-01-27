"""Create custody_events table

Revision ID: 003_create_custody_events
Revises: 002_create_kits
Create Date: 2026-01-27 00:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_create_custody_events'
down_revision: Union[str, None] = '002_create_kits'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create custody_events table
    op.create_table(
        'custody_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        # Event type enum
        sa.Column('event_type', sa.Enum('checkout_onprem', 'checkout_offsite', 'checkin', 'transfer', 'lost', name='custodyeventtype'), nullable=False),
        # Kit reference
        sa.Column('kit_id', sa.Integer(), nullable=False),
        # Who initiated the action
        sa.Column('initiated_by_id', sa.Integer(), nullable=False),
        sa.Column('initiated_by_name', sa.String(length=200), nullable=False),
        # Who receives custody
        sa.Column('custodian_id', sa.Integer(), nullable=True),
        sa.Column('custodian_name', sa.String(length=200), nullable=False),
        # Optional notes
        sa.Column('notes', sa.String(length=1000), nullable=True),
        # Location type
        sa.Column('location_type', sa.String(length=50), nullable=False),
        # Constraints
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['initiated_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['custodian_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes
    op.create_index(op.f('ix_custody_events_id'), 'custody_events', ['id'], unique=False)
    op.create_index(op.f('ix_custody_events_kit_id'), 'custody_events', ['kit_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and table
    op.drop_index(op.f('ix_custody_events_kit_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_id'), table_name='custody_events')
    op.drop_table('custody_events')
    op.execute('DROP TYPE custodyeventtype')
