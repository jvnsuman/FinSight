"""
Permanently deletes any account whose 30-day (default) soft-delete grace
period has passed. Safe to run repeatedly - only touches accounts that are
already is_active=False with an expired deletion_requested_at.

Run from the project root:
    python -m backend.scripts.purge_deleted_accounts
    python -m backend.scripts.purge_deleted_accounts --grace-days 7   # override
    python -m backend.scripts.purge_deleted_accounts --dry-run        # just report the count

Wire this into a daily cron job (or an APScheduler interval job, matching
the pattern used elsewhere in this codebase for background jobs) once
you've decided how deletion should actually run in production - this script
is deliberately standalone for now so it can be exercised and tested on its
own first.
"""
import argparse
import logging

from backend.database import SessionLocal
from backend.services.account_cleanup_service import (
    purge_expired_deleted_accounts,
    DEFAULT_GRACE_PERIOD_DAYS,
)

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grace-days", type=int, default=DEFAULT_GRACE_PERIOD_DAYS,
        help=f"Grace period in days before a soft-deleted account is hard-deleted (default: {DEFAULT_GRACE_PERIOD_DAYS})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report how many accounts WOULD be purged, without deleting anything",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.dry_run:
            from datetime import datetime, timedelta, timezone
            from backend.models.user import User
            cutoff = datetime.now(timezone.utc) - timedelta(days=args.grace_days)
            count = (
                db.query(User)
                .filter(
                    User.is_active == False,  # noqa: E712
                    User.deletion_requested_at.isnot(None),
                    User.deletion_requested_at < cutoff,
                )
                .count()
            )
            print(f"[dry run] {count} account(s) would be permanently deleted (grace period: {args.grace_days} days)")
        else:
            count = purge_expired_deleted_accounts(db, grace_period_days=args.grace_days)
            print(f"Permanently deleted {count} account(s)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
