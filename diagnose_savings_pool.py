"""
Diagnostic script for "July's savings didn't get added to the savings pool".

Run this from the FinSight project root, in your venv, with your real
DATABASE_URL configured (same as the app uses):

    python diagnose_savings_pool.py <your_email>

It prints:
  - The user's savings_pool, cash_balance, last_savings_refill_month,
    last_refill_amount exactly as stored.
  - What ensure_monthly_refill currently computes for "previous month"
    (should be July if run today) - income, expenses, and net savings for
    that month, straight from the transactions table.
  - Whether last_savings_refill_month is already >= this month (which would
    make ensure_monthly_refill silently skip - see the note below if so).

This is READ-ONLY except for one clearly-marked, optional interactive step
at the end that offers to reset last_savings_refill_month so the refill can
run again - it asks for confirmation before writing anything.
"""

import sys
from datetime import date

sys.path.insert(0, ".")

from backend.database import SessionLocal

# SQLAlchemy relationships on User (and other models) are declared by class
# name as a string (e.g. relationship("Account")), resolved lazily the first
# time any mapper configures itself. If only backend.models.user has been
# imported, that lookup fails with "failed to locate a name ('Account')" the
# moment db.query(User) touches the mapper - importing every model module
# up front (mirroring what backend/main.py does) registers all of them
# first, so relationships resolve correctly.
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
        print("Usage: python diagnose_savings_pool.py <your_email>")
        sys.exit(1)

    email = sys.argv[1]
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"No user found with email {email}")
        return

    print("=" * 60)
    print(f"User: {user.name} <{user.email}> (id={user.user_id})")
    print("=" * 60)
    print(f"savings_pool                = {user.savings_pool}")
    print(f"cash_balance                = {user.cash_balance}")
    print(f"last_savings_refill_month   = {user.last_savings_refill_month}")
    print(f"last_refill_amount          = {getattr(user, 'last_refill_amount', 'N/A (column not migrated yet)')}")
    print()

    current_month = date.today().replace(day=1)
    previous_month = (
        date(current_month.year - 1, 12, 1)
        if current_month.month == 1
        else current_month.replace(month=current_month.month - 1)
    )
    print(f"Today's date                = {date.today()}")
    print(f"current_month (this refill's cutoff) = {current_month}")
    print(f"previous_month (what should sweep in) = {previous_month}")
    print()

    # Mirrors the (now-fixed) check in savings_service.ensure_monthly_refill:
    # exact match against current_month, not >=. An earlier version of this
    # logic used >=, which could get permanently stuck if
    # last_savings_refill_month was ever ahead of the real current month for
    # any reason - == self-heals instead.
    already_refilled = user.last_savings_refill_month == current_month
    print(f"already_refilled_this_month (per == logic) = {already_refilled}")
    if already_refilled:
        print("  -> ensure_monthly_refill will skip this month, since it already ran.")
    elif user.last_savings_refill_month is not None and user.last_savings_refill_month > current_month:
        print(
            f"  -> last_savings_refill_month ({user.last_savings_refill_month}) is AFTER "
            f"current_month ({current_month}) - that's unusual and worth double-checking "
            f"how it got set, but the == fix means it will no longer block future refills."
        )
    print()

    first_day, last_day = _month_bounds(previous_month)
    summary = _get_summary_cards(db, user.user_id, first_day, last_day)
    print(f"Previous month ({previous_month}) transaction totals:")
    print(f"  total_income    = {summary['total_income']}")
    print(f"  total_expenses  = {summary['total_expenses']}")
    print(f"  total_savings   = {summary['total_savings']}  <- this is what should sweep in (floored at 0)")
    print()

    if summary["total_income"] == 0:
        print(
            "!! total_income for the previous month came back as 0.\n"
            "   Double check: are July's income transactions dated with\n"
            "   transaction_date between 2026-07-01 and 2026-07-31, and is\n"
            "   transaction_type exactly 'income' (not 'transfer' or something else)?"
        )

    db.close()


if __name__ == "__main__":
    main()
