"""add_user_role

Revision ID: 1409288b69b3
Revises: add_dhcp_pool
Create Date: 2026-01-06 09:19:29.859416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1409288b69b3'
down_revision = 'add_dhcp_pool'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column with default value 'RO'
    op.add_column('users', sa.Column('role', sa.String(10), nullable=False, server_default='RO'))

    # Update existing admin user to have ADMIN role
    op.execute("UPDATE users SET role = 'ADMIN' WHERE is_admin = 1")


def downgrade() -> None:
    # Remove role column
    op.drop_column('users', 'role')
