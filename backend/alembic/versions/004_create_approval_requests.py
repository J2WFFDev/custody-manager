"""Create approval_requests table

Revision ID: 004_create_approval_requests
Revises: 003_create_custody_events
Create Date: 2026-01-27 00:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_create_approval_requests'
down_revision: Union[str, None] = '003_create_custody_events'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create approval_requests table
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        # Kit reference
        sa.Column('kit_id', sa.Integer(), nullable=False),
        # Requester (e.g., Parent)
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('requester_name', sa.String(length=200), nullable=False),
        # Custodian (e.g., athlete/child)
        sa.Column('custodian_id', sa.Integer(), nullable=True),
        sa.Column('custodian_name', sa.String(length=200), nullable=False),
        # Approval status
        sa.Column('status', sa.Enum('pending', 'approved', 'denied', name='approvalstatus'), nullable=False),
        # Approver details (Armorer or Coach)
        sa.Column('approver_id', sa.Integer(), nullable=True),
        sa.Column('approver_name', sa.String(length=200), nullable=True),
        sa.Column('approver_role', sa.String(length=50), nullable=True),
        # Request details
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('denial_reason', sa.String(length=500), nullable=True),
        # Constraints
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['custodian_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes
    op.create_index(op.f('ix_approval_requests_id'), 'approval_requests', ['id'], unique=False)
    op.create_index(op.f('ix_approval_requests_kit_id'), 'approval_requests', ['kit_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and table
    op.drop_index(op.f('ix_approval_requests_kit_id'), table_name='approval_requests')
    op.drop_index(op.f('ix_approval_requests_id'), table_name='approval_requests')
    op.drop_table('approval_requests')
    # Drop enum type - use DROP TYPE IF EXISTS for safety
    op.execute('DROP TYPE IF EXISTS approvalstatus')
