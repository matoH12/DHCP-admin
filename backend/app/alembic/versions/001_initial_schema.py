"""Initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-06 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='RW'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Create ip_ranges table
    op.create_table('ip_ranges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('network_address', sa.String(length=15), nullable=False),
        sa.Column('cidr', sa.Integer(), nullable=False),
        sa.Column('gateway', sa.String(length=15), nullable=False),
        sa.Column('dns_servers', sa.Text(), nullable=True),
        sa.Column('domain_name', sa.String(length=255), nullable=True),
        sa.Column('pool_start', sa.String(length=15), nullable=True),
        sa.Column('pool_end', sa.String(length=15), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create devices table
    op.create_table('devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hostname', sa.String(length=63), nullable=False),
        sa.Column('mac_address', sa.String(length=17), nullable=False),
        sa.Column('ip_address', sa.String(length=15), nullable=False),
        sa.Column('ip_range_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ip_range_id'], ['ip_ranges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hostname'),
        sa.UniqueConstraint('mac_address'),
        sa.UniqueConstraint('ip_address')
    )

    # Create dhcp_configs table
    op.create_table('dhcp_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('config_content', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(length=255), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('generated_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create syslog_messages table
    op.create_table('syslog_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('facility', sa.String(length=50), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('hostname', sa.String(length=255), nullable=True),
        sa.Column('source_ip', sa.String(length=50), nullable=True),
        sa.Column('program', sa.String(length=100), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('raw_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_syslog_timestamp', 'syslog_messages', ['timestamp'])
    op.create_index('ix_syslog_severity', 'syslog_messages', ['severity'])
    op.create_index('ix_syslog_program', 'syslog_messages', ['program'])
    op.create_index('ix_syslog_hostname', 'syslog_messages', ['hostname'])
    op.create_index('ix_syslog_source_ip', 'syslog_messages', ['source_ip'])

    # Create settings table
    op.create_table('settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )


def downgrade():
    op.drop_table('settings')
    op.drop_index('ix_syslog_source_ip', 'syslog_messages')
    op.drop_index('ix_syslog_hostname', 'syslog_messages')
    op.drop_index('ix_syslog_program', 'syslog_messages')
    op.drop_index('ix_syslog_severity', 'syslog_messages')
    op.drop_index('ix_syslog_timestamp', 'syslog_messages')
    op.drop_table('syslog_messages')
    op.drop_table('dhcp_configs')
    op.drop_table('devices')
    op.drop_table('ip_ranges')
    op.drop_table('users')
