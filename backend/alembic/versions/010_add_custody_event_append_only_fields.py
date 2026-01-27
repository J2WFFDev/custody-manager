"""Add append-only fields to custody_events

Revision ID: 010_add_custody_event_append_only_fields
Revises: 009_add_performance_indexes
Create Date: 2026-01-27

Adds fields to custody_events table to support CUSTODY-015:
- approved_by_id: Foreign key to users table for approver
- approved_by_name: Name of approver for audit trail
- attestation_text: Legal text presented to user
- attestation_signature: Digital signature/acknowledgment
- attestation_timestamp: When user acknowledged
- attestation_ip_address: IP address for audit trail

These fields complete the append-only audit trail requirements.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '010_add_custody_event_append_only_fields'
down_revision = '009_add_performance_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Add approved_by fields
    op.add_column('custody_events', sa.Column('approved_by_id', sa.Integer(), nullable=True))
    op.add_column('custody_events', sa.Column('approved_by_name', sa.String(length=200), nullable=True))
    
    # Add attestation fields
    op.add_column('custody_events', sa.Column('attestation_text', sa.Text(), nullable=True))
    op.add_column('custody_events', sa.Column('attestation_signature', sa.String(length=200), nullable=True))
    op.add_column('custody_events', sa.Column('attestation_timestamp', sa.DateTime(), nullable=True))
    op.add_column('custody_events', sa.Column('attestation_ip_address', sa.String(length=45), nullable=True))
    
    # Add foreign key constraint for approved_by_id
    op.create_foreign_key(
        'fk_custody_events_approved_by_id_users',
        'custody_events', 'users',
        ['approved_by_id'], ['id']
    )
    
    # Add index on approved_by_id for query performance
    op.create_index('ix_custody_events_approved_by_id', 'custody_events', ['approved_by_id'], unique=False)


def downgrade():
    # Drop index and foreign key
    op.drop_index('ix_custody_events_approved_by_id', table_name='custody_events')
    op.drop_constraint('fk_custody_events_approved_by_id_users', 'custody_events', type_='foreignkey')
    
    # Drop columns in reverse order
    op.drop_column('custody_events', 'attestation_ip_address')
    op.drop_column('custody_events', 'attestation_timestamp')
    op.drop_column('custody_events', 'attestation_signature')
    op.drop_column('custody_events', 'attestation_text')
    op.drop_column('custody_events', 'approved_by_name')
    op.drop_column('custody_events', 'approved_by_id')
