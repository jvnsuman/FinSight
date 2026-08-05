"""add is_default to accounts for the system-seeded Cash Amount wallet

Revision ID: d4c8f2a6b103
Revises: c3f9a7e1d824
Create Date: 2026-08-02 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4c8f2a6b103'
down_revision: Union[str, Sequence[str], None] = 'c3f9a7e1d824'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('accounts', sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('accounts', 'is_default')
