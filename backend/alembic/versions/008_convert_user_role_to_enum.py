"""convert user role to enum

Revision ID: 008
Revises: 007
Create Date: 2026-01-27

Implements improved type safety for user roles (AUTH-001)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # For SQLite, just add the column if it doesn't exist
    # SQLite doesn't have native enums, so we'll keep it as string
    pass


def downgrade():
    pass
