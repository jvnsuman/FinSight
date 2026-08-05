"""
One-time correction script: backfills July's savings into the savings pool
for a user whose monthly refill already ran (and stamped itself done) before
July's transactions were fully in place, so it swept in 0 instead of the
real amount.

This is NOT something that should run automatically or repeatedly - it's a
manual, interactive, one-time fix for the specific situation of "the refill
already fired this month with a wrong/zero amount, and I know the correct
amount that should have been credited." Diagnose first with
diagnose_savings_pool.py to confirm the numbers before running this.

Usage:
    python fix_missed_refill.py <your_email>

It will:
  1. Show the user's current savings_pool, last_refill_amount, and what
     last month's real income-minus-expenses works out to.
  2. Ask for explicit confirmation before writing anything.
  3. If confirmed, adds the difference between what SHOULD have been swept
     in and what last_refill_amount actually shows was swept in, then
     updates last_refill_amount to the corrected value.

It does NOT touch cash_balance or last_savings_refill_month - those are
correct as-is (the wallet sweep itself worked fine; only the previous
month's income-minus-expenses portion was wrong).
"""

import sys
from decimal import Decimal
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
from backend.services.dashboard_service import _get_summary_cards, _month_bounds


def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_missed_refill.py <your_email>")
        sys.exit(1)

    email = sys.argv[1]
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"No user found with email {email}")
        db.close()
        return

    current_month = date.today().replace(day=1)
    previous_month = (
        date(current_month.year - 1, 12, 1)
        if current_month.month == 1
        else current_month.replace(month=current_month.month - 1)
    )

    if user.last_savings_refill_month != current_month:
        print(
            f"last_savings_refill_month is {user.last_savings_refill_month}, not {current_month} - "
            f"this user's refill for this month hasn't run (or already got fixed). "
            f"Nothing to correct; the normal ensure_monthly_refill flow will handle it correctly."
        )
        db.close()
        return

    first_day, last_day = _month_bounds(previous_month)
    summary = _get_summary_cards(db, user.user_id, first_day, last_day)
    correct_amount = Decimal(str(summary["total_savings"]))
    already_credited = Decimal(str(user.last_refill_amount))
    shortfall = correct_amount - already_credited

    print("=" * 60)
    print(f"User: {user.name} <{user.email}>")
    print(f"Previous month ({previous_month}) real net savings : {correct_amount}")
    print(f"Amount already credited (last_refill_amount)        : {already_credited}")
    print(f"Amount MISSING from savings_pool                    : {shortfall}")
    print(f"Current savings_pool                                : {user.savings_pool}")
    print(f"savings_pool AFTER correction would be              : {user.savings_pool + shortfall}")
    print("=" * 60)

    if shortfall <= 0:
        print("Nothing missing (shortfall is 0 or negative) - no correction needed.")
        db.close()
        return

    answer = input("\nApply this correction? Type 'yes' to proceed: ").strip().lower()
    if answer != "yes":
        print("Cancelled - no changes made.")
        db.close()
        return

    user.savings_pool = Decimal(user.savings_pool) + shortfall
    user.last_refill_amount = correct_amount
    db.commit()
    db.refresh(user)

    print(f"\nDone. savings_pool is now {user.savings_pool}, last_refill_amount is now {user.last_refill_amount}.")
    db.close()


if __name__ == "__main__":
    main()
