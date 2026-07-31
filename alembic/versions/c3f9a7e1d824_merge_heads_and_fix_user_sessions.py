"""merge heads (notifications, financial_health_cache, users columns)

This migration has THREE parents because three independent chains grew out
of the same branch point (e91b6f3a7d24) when different teammates worked in
parallel:

  - b8e2d5a913f7  (notifications: add action_url)
  - 2b9ef4897491  (financial_health_cache table)
  - f02c8a1d4b56  (users.is_active / users.deletion_requested_at columns)

f02c8a1d4b56 originally also tried to CREATE the user_sessions table, but
that table already existed in the shared database - created earlier by
a7d3f1c9b204 (a different branch off this same split). f02c8a1d4b56's
create_table step has been removed from that file to avoid a DuplicateTable
error.

NOTE: an earlier version of this migration also rewrote user_sessions'
columns (device_info -> device_label, is_active -> revoked, integer PK ->
string PK) to match backend/models/session.py + backend/routers/sessions.py.
That was a mistake: session.py/routers/sessions.py is an unfinished,
never-registered alternate session design (it isn't included in main.py,
and it imports a RevokeOthersResponse schema that doesn't even exist yet).
The table actually used in production is backend/models/user_session.py's
schema (device_info/is_active/integer PK), which a7d3f1c9b204 already
created correctly. This migration is now a plain merge with no schema
changes of its own - if/when the alternate session design is finished and
wired up, its migration should be written then, against whatever the
schema looks like at that point.

Revision ID: c3f9a7e1d824
Revises: b8e2d5a913f7, 2b9ef4897491, f02c8a1d4b56
Create Date: 2026-07-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f9a7e1d824'
down_revision: Union[str, Sequence[str], None] = ('b8e2d5a913f7', '2b9ef4897491', 'f02c8a1d4b56')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Pure merge point - no schema changes. See NOTE above.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
