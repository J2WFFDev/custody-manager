"""convert user role to enum

Revision ID: 007_convert_user_role_to_enum
Revises: 006_create_maintenance_events
Create Date: 2026-01-27

Implements improved type safety for user roles (AUTH-001)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_convert_user_role_to_enum'
down_revision = '006_create_maintenance_events'
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL: Create enum type and convert column
    # For databases that already have data, we need to:
    # 1. Create the enum type
    # 2. Convert the column using ALTER COLUMN with USING clause
    
    # Create the UserRole enum type
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'armorer', 'coach', 'volunteer', 'parent')")
    
    # Convert the role column to use the enum type
    # USING clause handles conversion from string to enum
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")


def downgrade():
    # Convert back to varchar
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR USING role::text")
    
    # Drop the enum type
    op.execute("DROP TYPE userrole")
