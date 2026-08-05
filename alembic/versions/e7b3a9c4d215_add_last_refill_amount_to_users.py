"""add last_refill_amount to users for savings pool breakdown display

Revision ID: e7b3a9c4d215
Revises: d4c8f2a6b103
Create Date: 2026-08-04 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b3a9c4d215'
down_revision: Union[str, Sequence[str], None] = 'd4c8f2a6b103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('last_refill_amount', sa.DECIMAL(14, 2), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_refill_amount')
