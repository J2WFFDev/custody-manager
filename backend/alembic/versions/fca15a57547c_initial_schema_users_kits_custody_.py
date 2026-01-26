"""Initial schema: users, kits, custody_events, maintenance_events

Revision ID: fca15a57547c
Revises: 
Create Date: 2026-01-26 22:56:17.498465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fca15a57547c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('oauth_provider', sa.String(length=50), nullable=False),
        sa.Column('oauth_id', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('verified_adult', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('oauth_provider', 'oauth_id', name='unique_oauth')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
    # Create kits table
    op.create_table(
        'kits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('qr_code', sa.String(length=255), nullable=False),
        sa.Column('serial_number_encrypted', sa.Text(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('current_custodian_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['current_custodian_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kits_current_custodian_id'), 'kits', ['current_custodian_id'], unique=False)
    op.create_index(op.f('ix_kits_id'), 'kits', ['id'], unique=False)
    op.create_index(op.f('ix_kits_qr_code'), 'kits', ['qr_code'], unique=True)
    op.create_index(op.f('ix_kits_status'), 'kits', ['status'], unique=False)
    
    # Create custody_events table
    op.create_table(
        'custody_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kit_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('from_user_id', sa.Integer(), nullable=True),
        sa.Column('to_user_id', sa.Integer(), nullable=True),
        sa.Column('approved_by_user_id', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('attestation_text', sa.Text(), nullable=True),
        sa.Column('attestation_signature', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('expected_return_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['approved_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custody_events_event_type'), 'custody_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_custody_events_from_user_id'), 'custody_events', ['from_user_id'], unique=False)
    op.create_index(op.f('ix_custody_events_id'), 'custody_events', ['id'], unique=False)
    op.create_index(op.f('ix_custody_events_kit_id'), 'custody_events', ['kit_id'], unique=False)
    op.create_index(op.f('ix_custody_events_to_user_id'), 'custody_events', ['to_user_id'], unique=False)
    op.create_index('ix_custody_events_created_at_desc', 'custody_events', [sa.text('created_at DESC')], unique=False)
    
    # Create maintenance_events table
    op.create_table(
        'maintenance_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kit_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('performed_by_user_id', sa.Integer(), nullable=False),
        sa.Column('round_count', sa.Integer(), nullable=True),
        sa.Column('parts_replaced', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('next_maintenance_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['kit_id'], ['kits.id'], ),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_events_event_type'), 'maintenance_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_maintenance_events_id'), 'maintenance_events', ['id'], unique=False)
    op.create_index(op.f('ix_maintenance_events_kit_id'), 'maintenance_events', ['kit_id'], unique=False)
    op.create_index('ix_maintenance_events_created_at_desc', 'maintenance_events', [sa.text('created_at DESC')], unique=False)
    
    # Add append-only rules for custody_events
    op.execute("""
        CREATE RULE custody_events_no_update AS ON UPDATE TO custody_events DO INSTEAD NOTHING;
    """)
    op.execute("""
        CREATE RULE custody_events_no_delete AS ON DELETE TO custody_events DO INSTEAD NOTHING;
    """)
    
    # Add append-only rules for maintenance_events
    op.execute("""
        CREATE RULE maintenance_events_no_update AS ON UPDATE TO maintenance_events DO INSTEAD NOTHING;
    """)
    op.execute("""
        CREATE RULE maintenance_events_no_delete AS ON DELETE TO maintenance_events DO INSTEAD NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop append-only rules for maintenance_events
    op.execute("DROP RULE IF EXISTS maintenance_events_no_delete ON maintenance_events;")
    op.execute("DROP RULE IF EXISTS maintenance_events_no_update ON maintenance_events;")
    
    # Drop append-only rules for custody_events
    op.execute("DROP RULE IF EXISTS custody_events_no_delete ON custody_events;")
    op.execute("DROP RULE IF EXISTS custody_events_no_update ON custody_events;")
    
    # Drop tables in reverse order
    op.drop_index('ix_maintenance_events_created_at_desc', table_name='maintenance_events')
    op.drop_index(op.f('ix_maintenance_events_kit_id'), table_name='maintenance_events')
    op.drop_index(op.f('ix_maintenance_events_id'), table_name='maintenance_events')
    op.drop_index(op.f('ix_maintenance_events_event_type'), table_name='maintenance_events')
    op.drop_table('maintenance_events')
    
    op.drop_index('ix_custody_events_created_at_desc', table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_to_user_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_kit_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_from_user_id'), table_name='custody_events')
    op.drop_index(op.f('ix_custody_events_event_type'), table_name='custody_events')
    op.drop_table('custody_events')
    
    op.drop_index(op.f('ix_kits_status'), table_name='kits')
    op.drop_index(op.f('ix_kits_qr_code'), table_name='kits')
    op.drop_index(op.f('ix_kits_id'), table_name='kits')
    op.drop_index(op.f('ix_kits_current_custodian_id'), table_name='kits')
    op.drop_table('kits')
    
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
