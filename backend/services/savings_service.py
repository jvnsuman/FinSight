"""
Savings pool service.

savings_pool is a persistent balance, separate from the trading cash_balance.
It is what goal allocations actually draw down (fixing the earlier bug where
allocating "from savings" grew a goal without shrinking anything), and it is
also what an over-budget expense draws down automatically before ever
touching a goal (see transaction_service.create_transaction).

Refill mechanics (see ensure_monthly_refill):
  - Once per calendar month (tracked via User.last_savings_refill_month),
    the pool is topped up by max(that month's income - expenses, 0) - a
    negative month contributes nothing rather than draining the pool.
  - At the same moment, the ENTIRE current cash_balance (trading wallet) is
    swept into the pool and cash_balance is reset to 0. This only happens
    once per month at refill time, not on every request - otherwise the
    wallet could never hold cash between refills for buying/selling.
  - The refill is applied lazily: whichever endpoint touches savings_pool
    first in a new calendar month triggers it. There is no background job.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.models.user import User


def ensure_monthly_refill(db: Session, user_id: int) -> User:
    """
    Checks whether this user's savings_pool has already been refilled for the
    current calendar month; if not, tops it up from last month's
    income-expenses plus a full sweep of cash_balance, then stamps
    last_savings_refill_month so it doesn't run again until next month.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found")

    current_month = date.today().replace(day=1)
    already_refilled_this_month = (
        user.last_savings_refill_month is not None
        and user.last_savings_refill_month >= current_month
    )
    if already_refilled_this_month:
        return user

    # Local import to avoid a circular import at module load time
    # (dashboard_service doesn't import savings_service).
    from backend.services.dashboard_service import _get_summary_cards, _month_bounds

    first_day, last_day = _month_bounds(current_month)
    summary = _get_summary_cards(db, user_id, first_day, last_day)
    month_net_savings = max(Decimal(str(summary["total_savings"])), Decimal("0"))

    swept_from_wallet = Decimal(user.cash_balance)

    user.savings_pool = Decimal(user.savings_pool) + month_net_savings + swept_from_wallet
    user.cash_balance = Decimal("0")
    user.last_savings_refill_month = current_month

    db.commit()
    db.refresh(user)
    return user


def get_savings_pool(db: Session, user_id: int) -> Decimal:
    user = ensure_monthly_refill(db, user_id)
    return user.savings_pool
