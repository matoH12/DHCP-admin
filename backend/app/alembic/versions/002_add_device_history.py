"""Add device history table

Revision ID: 002_add_device_history
Revises: 001_initial_schema
Create Date: 2026-01-06 18:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_device_history'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """
    Create device_history table for tracking device activity over time.

    This table records DHCP events (ACK, REQUEST) for analytics:
    - Activity timeline charts
    - Top active devices
    - Historical device behavior analysis

    Retention: 90 days (managed by cleanup job)
    """
    # Create device_history table
    op.create_table('device_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ip_address', sa.String(length=15), nullable=False),
        sa.Column('mac_address', sa.String(length=17), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create composite index for efficient device-specific timeline queries
    op.create_index(
        'idx_device_history_device_timestamp',
        'device_history',
        ['device_id', 'timestamp']
    )

    # Create index on timestamp for aggregation queries across all devices
    op.create_index(
        'idx_device_history_timestamp',
        'device_history',
        ['timestamp']
    )

    # Create index on device_id for faster foreign key lookups
    op.create_index(
        'idx_device_history_device_id',
        'device_history',
        ['device_id']
    )


def downgrade():
    """Remove device_history table and indexes"""
    op.drop_index('idx_device_history_device_id', table_name='device_history')
    op.drop_index('idx_device_history_timestamp', table_name='device_history')
    op.drop_index('idx_device_history_device_timestamp', table_name='device_history')
    op.drop_table('device_history')
