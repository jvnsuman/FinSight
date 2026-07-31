"""add action_url to notifications for click-through actions

Revision ID: b8e2d5a913f7
Revises: a7d3f1c9b204
Create Date: 2026-07-29 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8e2d5a913f7'
down_revision: Union[str, Sequence[str], None] = 'a7d3f1c9b204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notifications', sa.Column('action_url', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('notifications', 'action_url')
