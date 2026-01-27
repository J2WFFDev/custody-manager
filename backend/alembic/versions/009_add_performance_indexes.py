"""add performance indexes

Revision ID: 009_add_performance_indexes
Revises: 008_add_encrypted_serial_number
Create Date: 2026-01-27

Adds indexes for common query patterns to improve performance:
- approval_requests.status for filtering pending/approved requests
- maintenance_events.is_open for finding active maintenance
- custody_events.event_type for filtering by event type
- users.role for role-based queries
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_add_performance_indexes'
down_revision = '008_add_encrypted_serial_number'
branch_labels = None
depends_on = None


def upgrade():
    # Add index on approval_requests.status for filtering pending/approved/denied requests
    op.create_index('ix_approval_requests_status', 'approval_requests', ['status'], unique=False)
    
    # Add index on maintenance_events.is_open for finding active maintenance events
    op.create_index('ix_maintenance_events_is_open', 'maintenance_events', ['is_open'], unique=False)
    
    # Add index on custody_events.event_type for filtering by event type
    op.create_index('ix_custody_events_event_type', 'custody_events', ['event_type'], unique=False)
    
    # Add index on users.role for role-based queries (e.g., finding all armorers)
    op.create_index('ix_users_role', 'users', ['role'], unique=False)
    
    # Add composite index on custody_events (kit_id, created_at) for efficient timeline queries
    op.create_index('ix_custody_events_kit_id_created_at', 'custody_events', ['kit_id', 'created_at'], unique=False)


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('ix_custody_events_kit_id_created_at', table_name='custody_events')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_custody_events_event_type', table_name='custody_events')
    op.drop_index('ix_maintenance_events_is_open', table_name='maintenance_events')
    op.drop_index('ix_approval_requests_status', table_name='approval_requests')
