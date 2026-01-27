"""create maintenance events table and add expected_return_date

Revision ID: 006_create_maintenance_events
Revises: 005_add_attestation_fields
Create Date: 2026-01-27
"""
from alembic import op
import sqlalchemy as sa

revision = '006_create_maintenance_events'
down_revision = '005_add_attestation_fields'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add expected_return_date to custody_events table
    op.add_column('custody_events', sa.Column('expected_return_date', sa.Date(), nullable=True))
    
    # Add expected_return_date to approval_requests table
    op.add_column('approval_requests', sa.Column('expected_return_date', sa.Date(), nullable=True))
    
    # Create maintenance_events table
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
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['opened_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'])
    )
    op.create_index(op.f('ix_maintenance_events_id'), 'maintenance_events', ['id'], unique=False)
    op.create_index(op.f('ix_maintenance_events_kit_id'), 'maintenance_events', ['kit_id'], unique=False)

def downgrade() -> None:
    # Drop maintenance_events table
    op.drop_index(op.f('ix_maintenance_events_kit_id'), table_name='maintenance_events')
    op.drop_index(op.f('ix_maintenance_events_id'), table_name='maintenance_events')
    op.drop_table('maintenance_events')
    
    # Remove expected_return_date from approval_requests
    op.drop_column('approval_requests', 'expected_return_date')
    
    # Remove expected_return_date from custody_events
    op.drop_column('custody_events', 'expected_return_date')
