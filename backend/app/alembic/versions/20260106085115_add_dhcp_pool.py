"""add dhcp pool to ip_range

Revision ID: add_dhcp_pool
Revises: 
Create Date: 2026-01-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_dhcp_pool'
down_revision = None


def upgrade():
    op.add_column('ip_ranges', sa.Column('pool_start', sa.String(15), nullable=True))
    op.add_column('ip_ranges', sa.Column('pool_end', sa.String(15), nullable=True))


def downgrade():
    op.drop_column('ip_ranges', 'pool_end')
    op.drop_column('ip_ranges', 'pool_start')
