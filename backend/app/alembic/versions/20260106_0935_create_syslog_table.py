"""create_syslog_table

Revision ID: create_syslog_table
Revises: 1409288b69b3
Create Date: 2026-01-06 09:35:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_syslog_table'
down_revision = '1409288b69b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create syslog_messages table
    op.create_table(
        'syslog_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('facility', sa.String(50), nullable=True),
        sa.Column('severity', sa.String(20), nullable=True),
        sa.Column('hostname', sa.String(255), nullable=True),
        sa.Column('source_ip', sa.String(50), nullable=True),
        sa.Column('program', sa.String(100), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('raw_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_syslog_messages_id', 'syslog_messages', ['id'])
    op.create_index('ix_syslog_messages_timestamp', 'syslog_messages', ['timestamp'])
    op.create_index('ix_syslog_messages_severity', 'syslog_messages', ['severity'])
    op.create_index('ix_syslog_messages_hostname', 'syslog_messages', ['hostname'])
    op.create_index('ix_syslog_messages_source_ip', 'syslog_messages', ['source_ip'])
    op.create_index('ix_syslog_messages_program', 'syslog_messages', ['program'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_syslog_messages_program', 'syslog_messages')
    op.drop_index('ix_syslog_messages_source_ip', 'syslog_messages')
    op.drop_index('ix_syslog_messages_hostname', 'syslog_messages')
    op.drop_index('ix_syslog_messages_severity', 'syslog_messages')
    op.drop_index('ix_syslog_messages_timestamp', 'syslog_messages')
    op.drop_index('ix_syslog_messages_id', 'syslog_messages')

    # Drop table
    op.drop_table('syslog_messages')
