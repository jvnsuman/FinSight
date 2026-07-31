"""add account deactivation columns to users

Revision ID: f02c8a1d4b56
Revises: e91b6f3a7d24
Create Date: 2026-07-29 00:00:00.000000

NOTE (amended after a multi-head merge investigation): this migration
originally also created the user_sessions table. That create_table step has
been REMOVED here - user_sessions already exists in the shared database
(created earlier by a7d3f1c9b204, on a different branch of this same
e91b6f3a7d24 split) with an older column layout (device_info/is_active,
integer PK). Re-running create_table against a DB that already has this
table fails with DuplicateTable.

The correction of user_sessions' existing columns to match what this
migration originally intended (device_label/revoked, string PK) now happens
in the merge migration c3f9a7e1d824, which is the point where all three
branches (this one, the notifications chain, and financial_health_cache)
reunite - that's the only place that can safely assume every branch's
"has create_table already run for this table under some other revision?"
question has been answered.

This migration keeps ONLY the users.is_active / users.deletion_requested_at
columns, since those are genuinely new and not created by any other branch.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f02c8a1d4b56'
down_revision: Union[str, Sequence[str], None] = 'e91b6f3a7d24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.add_column(
        'users',
        sa.Column('deletion_requested_at', sa.TIMESTAMP(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'deletion_requested_at')
    op.drop_column('users', 'is_active')
