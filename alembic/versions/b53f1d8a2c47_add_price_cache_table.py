"""add price_cache table

Revision ID: b53f1d8a2c47
Revises: a429c396ee12
Create Date: 2026-07-16 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b53f1d8a2c47'
down_revision: Union[str, Sequence[str], None] = 'a429c396ee12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'price_cache',
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('price', sa.DECIMAL(precision=14, scale=4), nullable=False),
        sa.Column('previous_close', sa.DECIMAL(precision=14, scale=4), nullable=True),
        sa.Column('latest_trading_day', sa.String(length=20), nullable=True),
        sa.Column('fetched_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('symbol'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('price_cache')
