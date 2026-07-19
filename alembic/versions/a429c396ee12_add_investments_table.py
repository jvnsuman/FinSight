"""add investments table

Revision ID: a429c396ee12
Revises: a18d06e7e499
Create Date: 2026-07-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a429c396ee12'
down_revision: Union[str, Sequence[str], None] = 'a18d06e7e499'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'investments',
        sa.Column('investment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.String(length=20), nullable=False),
        sa.Column('asset_name', sa.String(length=150), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=True),
        sa.Column('quantity', sa.DECIMAL(precision=18, scale=4), nullable=False),
        sa.Column('purchase_price', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('purchase_date', sa.DATE(), nullable=False),
        sa.Column('notes', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('investment_id'),
    )
    op.create_index(op.f('ix_investments_investment_id'), 'investments', ['investment_id'], unique=False)
    op.create_index(op.f('ix_investments_user_id'), 'investments', ['user_id'], unique=False)
    op.create_index(op.f('ix_investments_symbol'), 'investments', ['symbol'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_investments_symbol'), table_name='investments')
    op.drop_index(op.f('ix_investments_user_id'), table_name='investments')
    op.drop_index(op.f('ix_investments_investment_id'), table_name='investments')
    op.drop_table('investments')
