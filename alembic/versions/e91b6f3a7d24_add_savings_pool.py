"""add savings pool to users

Revision ID: e91b6f3a7d24
Revises: d78a4e5f9c12
Create Date: 2026-07-17 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e91b6f3a7d24'
down_revision: Union[str, Sequence[str], None] = 'd78a4e5f9c12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('savings_pool', sa.DECIMAL(precision=14, scale=2), nullable=False, server_default='0'),
    )
    op.add_column(
        'users',
        sa.Column('last_savings_refill_month', sa.DATE(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'last_savings_refill_month')
    op.drop_column('users', 'savings_pool')
