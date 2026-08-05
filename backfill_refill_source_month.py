"""
One-time backfill: sets last_refill_source_month for users whose refill ran
before that column existed, so the savings breakdown popup correctly labels
"Added from <month>" with the month the money actually came from (e.g. July
for an August-triggered refill), instead of showing blank or the wrong month.

Safe to run more than once - it only fills in last_refill_source_month when
it's still null and last_savings_refill_month is set; already-correct rows
are left untouched.

Usage:
    python backfill_refill_source_month.py <your_email>
"""

import sys
from datetime import date

sys.path.insert(0, ".")

from backend.database import SessionLocal

# See diagnose_savings_pool.py for why every model needs importing up front.
from backend.models import user as _user_model            # noqa: F401
from backend.models import account as _account_model       # noqa: F401
from backend.models import category as _category_model     # noqa: F401
from backend.models import transaction as _transaction_model  # noqa: F401
from backend.models import budget as _budget_model          # noqa: F401
from backend.models import investment as _investment_model  # noqa: F401
from backend.models import price_cache as _price_cache_model  # noqa: F401
from backend.models import goal as _goal_model  # noqa: F401
from backend.models import trade as _trade_model  # noqa: F401
from backend.models import notification as _notification_model  # noqa: F401
from backend.models import user_session as _user_session_model  # noqa: F401
from backend.models import financial_health as _financial_health_model  # noqa: F401

from backend.models.user import User


def main():
    if len(sys.argv) < 2:
        print("Usage: python backfill_refill_source_month.py <your_email>")
        sys.exit(1)

    email = sys.argv[1]
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"No user found with email {email}")
        db.close()
        return

    if not user.last_savings_refill_month:
        print("last_savings_refill_month is not set - nothing to backfill.")
        db.close()
        return

    if user.last_refill_source_month:
        print(f"last_refill_source_month is already set to {user.last_refill_source_month} - nothing to do.")
        db.close()
        return

    trigger_month = user.last_savings_refill_month
    source_month = (
        date(trigger_month.year - 1, 12, 1)
        if trigger_month.month == 1
        else trigger_month.replace(month=trigger_month.month - 1)
    )

    print(f"last_savings_refill_month : {trigger_month}")
    print(f"-> setting last_refill_source_month to : {source_month}")

    user.last_refill_source_month = source_month
    db.commit()
    db.refresh(user)

    print("Done.")
    db.close()


if __name__ == "__main__":
    main()
