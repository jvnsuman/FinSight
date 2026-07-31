"""
Hard-delete cleanup for soft-deleted accounts.

deactivate_account() (auth_service.py) only soft-deletes: is_active=False,
deletion_requested_at stamped, all sessions killed. This module finds
accounts whose grace period has expired and actually removes them, along
with everything the User model cascades onto (accounts, transactions,
budgets, investments, goals, trades, sessions).

Run manually (python -m backend.scripts.purge_deleted_accounts) or on a
schedule (e.g. a daily cron job / APScheduler interval job) - it's
idempotent, so running it more often than needed is harmless.
"""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.models.user import User

logger = logging.getLogger("finsight.account_cleanup")

DEFAULT_GRACE_PERIOD_DAYS = 30


def purge_expired_deleted_accounts(db: Session, grace_period_days: int = DEFAULT_GRACE_PERIOD_DAYS) -> int:
    """
    Permanently deletes every account that was soft-deleted more than
    `grace_period_days` ago. Returns the number of accounts purged.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=grace_period_days)

    expired_users = (
        db.query(User)
        .filter(
            User.is_active == False,  # noqa: E712
            User.deletion_requested_at.isnot(None),
            User.deletion_requested_at < cutoff,
        )
        .all()
    )

    for user in expired_users:
        logger.info("Purging account user_id=%s (deleted %s ago)", user.user_id, grace_period_days)
        db.delete(user)  # cascades via the relationships defined on User

    db.commit()
    return len(expired_users)
