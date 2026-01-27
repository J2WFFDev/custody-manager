"""Add attestation fields to approval_requests

Revision ID: 005_add_attestation_fields
Revises: 004_create_approval_requests
Create Date: 2026-01-27

Implements CUSTODY-012: Responsibility attestation for off-site custody
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_attestation_fields'
down_revision = '004_create_approval_requests'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add attestation fields to approval_requests table
    op.add_column('approval_requests', sa.Column('attestation_text', sa.Text(), nullable=True))
    op.add_column('approval_requests', sa.Column('attestation_signature', sa.String(length=200), nullable=True))
    op.add_column('approval_requests', sa.Column('attestation_timestamp', sa.DateTime(), nullable=True))
    op.add_column('approval_requests', sa.Column('attestation_ip_address', sa.String(length=45), nullable=True))


def downgrade() -> None:
    # Remove attestation fields from approval_requests table
    op.drop_column('approval_requests', 'attestation_ip_address')
    op.drop_column('approval_requests', 'attestation_timestamp')
    op.drop_column('approval_requests', 'attestation_signature')
    op.drop_column('approval_requests', 'attestation_text')
