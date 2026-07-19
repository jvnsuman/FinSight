"""add cash_balance to users and trades table

Revision ID: d78a4e5f9c12
Revises: c67e2f9b3d81
Create Date: 2026-07-17 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd78a4e5f9c12'
down_revision: Union[str, Sequence[str], None] = 'c67e2f9b3d81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('cash_balance', sa.DECIMAL(precision=14, scale=2), nullable=False, server_default='0'),
    )

    op.create_table(
        'trades',
        sa.Column('trade_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('investment_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=10), nullable=False),
        sa.Column('asset_type', sa.String(length=20), nullable=True),
        sa.Column('asset_name', sa.String(length=150), nullable=True),
        sa.Column('symbol', sa.String(length=20), nullable=True),
        sa.Column('quantity', sa.DECIMAL(precision=18, scale=4), nullable=True),
        sa.Column('price', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('cash_amount', sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column('trade_date', sa.DATE(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['investment_id'], ['investments.investment_id'], ),
        sa.PrimaryKeyConstraint('trade_id'),
    )
    op.create_index(op.f('ix_trades_trade_id'), 'trades', ['trade_id'], unique=False)
    op.create_index(op.f('ix_trades_user_id'), 'trades', ['user_id'], unique=False)
    op.create_index(op.f('ix_trades_investment_id'), 'trades', ['investment_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_trades_investment_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_user_id'), table_name='trades')
    op.drop_index(op.f('ix_trades_trade_id'), table_name='trades')
    op.drop_table('trades')
    op.drop_column('users', 'cash_balance')
