"""add goals table

Revision ID: c67e2f9b3d81
Revises: b53f1d8a2c47
Create Date: 2026-07-17 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c67e2f9b3d81'
down_revision: Union[str, Sequence[str], None] = 'b53f1d8a2c47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'goals',
        sa.Column('goal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('goal_name', sa.String(length=150), nullable=False),
        sa.Column('goal_type', sa.String(length=50), nullable=True),
        sa.Column('target_amount', sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column('current_amount', sa.DECIMAL(precision=14, scale=2), nullable=False),
        sa.Column('target_date', sa.DATE(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('goal_id'),
    )
    op.create_index(op.f('ix_goals_goal_id'), 'goals', ['goal_id'], unique=False)
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_goals_user_id'), table_name='goals')
    op.drop_index(op.f('ix_goals_goal_id'), table_name='goals')
    op.drop_table('goals')
