"""add last_refill_source_month to users for correct savings breakdown labeling

Revision ID: f8c1d5e6a327
Revises: e7b3a9c4d215
Create Date: 2026-08-05 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8c1d5e6a327'
down_revision: Union[str, Sequence[str], None] = 'e7b3a9c4d215'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('last_refill_source_month', sa.DATE(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_refill_source_month')
