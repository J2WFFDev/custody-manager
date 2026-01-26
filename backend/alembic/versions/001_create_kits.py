"""create kits table

Revision ID: 001_create_kits
Revises: 
Create Date: 2026-01-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_create_kits'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create kits table
    op.create_table(
        'kits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        # Enum values match KitStatus in app.models.kit
        sa.Column('status', sa.Enum('available', 'checked_out', 'in_maintenance', 'lost', name='kitstatus'), nullable=False),
        sa.Column('current_custodian_id', sa.Integer(), nullable=True),
        sa.Column('current_custodian_name', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kits_code'), 'kits', ['code'], unique=True)
    op.create_index(op.f('ix_kits_id'), 'kits', ['id'], unique=False)


def downgrade() -> None:
    # Drop indexes and table
    op.drop_index(op.f('ix_kits_id'), table_name='kits')
    op.drop_index(op.f('ix_kits_code'), table_name='kits')
    op.drop_table('kits')
    op.execute('DROP TYPE kitstatus')
