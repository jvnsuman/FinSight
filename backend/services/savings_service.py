"""
Savings pool service.

savings_pool is a persistent balance, separate from the trading cash_balance.
It is what goal allocations actually draw down (fixing the earlier bug where
allocating "from savings" grew a goal without shrinking anything), and it is
also what an over-budget expense draws down automatically before ever
touching a goal (see transaction_service.create_transaction).

Refill mechanics (see ensure_monthly_refill):
  - Once per calendar month (tracked via User.last_savings_refill_month),
    the pool is topped up by max(the PREVIOUS month's income - expenses, 0) -
    a negative month contributes nothing rather than draining the pool.
    It's the previous month specifically (not the current one) because the
    current month has usually barely started when the refill fires, so it
    wouldn't have meaningful savings to sweep yet.
  - At the same moment, the ENTIRE current cash_balance (trading wallet) is
    swept into the pool and cash_balance is reset to 0. This only happens
    once per month at refill time, not on every request - otherwise the
    wallet could never hold cash between refills for buying/selling.
  - The exact amount added at that refill (previous month's savings + swept
    wallet cash) is stamped onto User.last_refill_amount, purely so the
    savings breakdown popup can show "added from last month" as its own
    line instead of just the running total.
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
    current calendar month; if not, tops it up from the PREVIOUS month's
    income-expenses (the month that just finished) plus a full sweep of
    cash_balance, then stamps last_savings_refill_month so it doesn't run
    again until next month.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found")

    current_month = date.today().replace(day=1)
    # Exact match, not >= : if last_savings_refill_month is somehow ahead of
    # current_month (a bad manual edit, a past bug, a wrong system clock at
    # some point), >= would treat that as "already done" forever, with no
    # way to self-heal short of a direct DB fix. == just re-runs the refill
    # instead - safe to do even if it re-fires, since ensure_monthly_refill
    # only ever sweeps the one previous month's savings, not a running total.
    already_refilled_this_month = user.last_savings_refill_month == current_month
    if already_refilled_this_month:
        return user

    # Local import to avoid a circular import at module load time
    # (dashboard_service doesn't import savings_service).
    from backend.services.dashboard_service import _get_summary_cards, _month_bounds

    # The month that just ended - NOT current_month, which has barely
    # started and would have ~0 savings to sweep. current_month is the
    # cutoff we stamp on last_savings_refill_month so this only fires once
    # per calendar month; previous_month is what we actually pull savings
    # from. A user's very first refill after registering mid-month still
    # only credits that previous month's activity, same as every refill
    # after it - there's no partial-month proration.
    previous_month = date(current_month.year - 1, 12, 1) if current_month.month == 1 \
        else current_month.replace(month=current_month.month - 1)

    first_day, last_day = _month_bounds(previous_month)
    summary = _get_summary_cards(db, user_id, first_day, last_day)
    month_net_savings = max(Decimal(str(summary["total_savings"])), Decimal("0"))

    swept_from_wallet = Decimal(user.cash_balance)
    total_refill_amount = month_net_savings + swept_from_wallet

    user.savings_pool = Decimal(user.savings_pool) + total_refill_amount
    user.cash_balance = Decimal("0")
    user.last_savings_refill_month = current_month
    user.last_refill_amount = total_refill_amount
    user.last_refill_source_month = previous_month

    db.commit()
    db.refresh(user)
    return user


def get_savings_pool(db: Session, user_id: int) -> Decimal:
    """
    Returns the pool total to DISPLAY to the user - the real stored
    savings_pool PLUS this calendar month's running contribution (income
    minus expenses so far), since that money is genuinely theirs to count as
    savings even though it hasn't been formally swept into the stored ledger
    yet (that sweep only happens once, at next month's refill).

    This is deliberately different from the stored User.savings_pool column,
    which other code (goal draws, the overspend shortfall check in
    transaction_service) should keep reading directly when it needs the real
    ledger balance that can actually be debited - not this display total,
    which includes money that's still just sitting in the wallet/accounts
    rather than in the pool itself.
    """
    user = ensure_monthly_refill(db, user_id)

    from backend.services.dashboard_service import _get_summary_cards, _month_bounds

    current_month = date.today().replace(day=1)
    first_day, last_day = _month_bounds(current_month)
    summary = _get_summary_cards(db, user_id, first_day, last_day)
    this_month_contribution = max(Decimal(str(summary["total_savings"])), Decimal("0"))

    return Decimal(user.savings_pool) + this_month_contribution


def get_savings_breakdown(db: Session, user_id: int) -> dict:
    """
    Builds the "what makes up my savings pool" breakdown for the detail
    popup on the dashboard's Savings Pool card.

    There's no ledger table recording every refill/allocation event, so this
    is composed from what's currently derivable: the pool total itself, this
    month's already-applied contribution, wallet cash still waiting for next
    month's sweep, and how much of the user's goal funding (Goal.
    current_amount) has already been drawn out of the pool.
    """
    from backend.models.goal import Goal
    from backend.services.dashboard_service import _get_summary_cards, _month_bounds

    user = ensure_monthly_refill(db, user_id)

    current_month = date.today().replace(day=1)
    first_day, last_day = _month_bounds(current_month)
    summary = _get_summary_cards(db, user_id, first_day, last_day)
    this_month_contribution = max(Decimal(str(summary["total_savings"])), Decimal("0"))

    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    goal_allocations = [
        {
            "goal_id": g.goal_id,
            "goal_name": g.goal_name,
            "current_amount": float(g.current_amount),
        }
        for g in goals
    ]
    total_allocated_to_goals = sum((Decimal(str(g["current_amount"])) for g in goal_allocations), Decimal("0"))

    # Same total shown on the dashboard's Savings Pool card - the stored
    # pool balance PLUS this month's running contribution, not just the
    # stored balance alone. Without this, the popup's "Total in pool" figure
    # at the top wouldn't match the sum of its own breakdown rows below it
    # (pool + this month's contribution + pending wallet cash).
    displayed_total = Decimal(user.savings_pool) + this_month_contribution

    return {
        "savings_pool": float(displayed_total),
        "this_month_contribution": float(this_month_contribution),
        "wallet_cash_pending_sweep": float(user.cash_balance),
        "total_allocated_to_goals": float(total_allocated_to_goals),
        "goal_allocations": goal_allocations,
        # When the top-up itself happened (e.g. August, since refills always
        # trigger at the start of the month they're touched in).
        "last_refill_triggered_month": user.last_savings_refill_month.isoformat() if user.last_savings_refill_month else None,
        # Which month's savings that top-up actually credited (e.g. July -
        # always one month before last_refill_triggered_month). This is the
        # one to show next to the credited amount ("Added from July"), not
        # the trigger month, or it mislabels July's savings as August's.
        "last_refill_month": user.last_refill_source_month.isoformat() if user.last_refill_source_month else None,
        "last_refill_amount": float(user.last_refill_amount),
    }
