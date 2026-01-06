"""create_settings_table

Revision ID: create_settings_table
Revises: create_syslog_table
Create Date: 2026-01-06 09:45:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_settings_table'
down_revision = 'create_syslog_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.String(500), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Create indexes
    op.create_index('ix_settings_id', 'settings', ['id'])
    op.create_index('ix_settings_key', 'settings', ['key'])

    # Insert default settings
    op.execute("""
        INSERT INTO settings (key, value, description) VALUES
        ('syslog_retention_days', '180', 'Počet dní uchovania syslog záznamov (default: 180 = 6 mesiacov)'),
        ('syslog_cleanup_enabled', 'true', 'Automatické mazanie starých logov (true/false)'),
        ('syslog_cleanup_hour', '2', 'Hodina spustenia čistenia logov (0-23)')
    """)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_settings_key', 'settings')
    op.drop_index('ix_settings_id', 'settings')

    # Drop table
    op.drop_table('settings')
