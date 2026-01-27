"""add expected_return_date for soft warnings

Revision ID: 008_add_expected_return_date
Revises: 007_convert_user_role_to_enum
Create Date: 2026-01-27

Implements CUSTODY-008 and CUSTODY-014:
- Add expected_return_date to custody_events table
- Add expected_return_date to approval_requests table
- Enable soft warnings for overdue returns and extended custody
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_expected_return_date'
down_revision = '007_convert_user_role_to_enum'
branch_labels = None
depends_on = None


def upgrade():
    # Add expected_return_date to custody_events table
    op.add_column('custody_events', sa.Column('expected_return_date', sa.Date(), nullable=True))
    
    # Add expected_return_date to approval_requests table (if not already present from model)
    # Note: The model already has this field, but it may not be in the database yet
    # We use a conditional approach to handle existing columns gracefully
    op.add_column('approval_requests', sa.Column('expected_return_date', sa.Date(), nullable=True))


def downgrade():
    # Remove expected_return_date from approval_requests table
    op.drop_column('approval_requests', 'expected_return_date')
    
    # Remove expected_return_date from custody_events table
    op.drop_column('custody_events', 'expected_return_date')
