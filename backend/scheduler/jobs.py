"""
Milestone 3 - Scheduled alert jobs (APScheduler)

These run outside any FastAPI request, so they use SessionLocal directly
(the same engine/session factory get_db() wraps for regular requests, but
without the request-scoped dependency injection) and always close/rollback
their own session in a finally block.
"""

import logging
from datetime import date, timedelta

from backend.database import SessionLocal
from backend.models.investment import Investment
from backend.models.user import User

logger = logging.getLogger("fap.scheduler")


def check_investment_price_moves() -> None:
    """
    Daily job: for every DISTINCT symbol currently held by any active
    investment, refresh its price via the existing cache-aware
    market_data_service.get_price() (which already respects the Alpha
    Vantage 25/day quota and falls back to cache when exhausted - this job
    does NOT bypass that), then check each holding for a significant
    single-day move and notify the owning user if so.

    Deliberately reuses get_price() rather than force-refreshing, so this
    job's calls count against and are throttled by the same shared daily
    quota as regular user-facing requests - it will not "starve" the app of
    its remaining Alpha Vantage calls, it just takes its normal share.
    """
    from backend.services import market_data_service, alert_service

    db = SessionLocal()
    try:
        holdings = db.query(Investment).filter(Investment.is_active.is_(True)).all()

        # Group by symbol first so a stock held by 5 users only costs 1 API
        # call, not 5 - previous_close is shared across users for the same
        # symbol anyway (see PriceCache's own docstring).
        symbols_seen = set()
        checked = 0

        for holding in holdings:
            if not holding.symbol:
                continue  # e.g. gold/cash holdings with no ticker - nothing to compare against

            price_row = market_data_service.get_price(db, holding.symbol)
            if price_row is None or price_row.previous_close is None:
                continue

            alert_service.check_investment_price_move(
                db=db,
                user_id=holding.user_id,
                asset_name=holding.asset_name,
                current_price=price_row.price,
                previous_close=price_row.previous_close,
            )
            symbols_seen.add(holding.symbol)
            checked += 1

        logger.info("check_investment_price_moves: checked %d holdings across %d symbols", checked, len(symbols_seen))
    except Exception:
        logger.exception("check_investment_price_moves job failed")
        db.rollback()
    finally:
        db.close()


def send_monthly_summaries() -> None:
    """
    Monthly job (scheduled to run on the 1st of each month): sends every
    user an in-app "here's your month" notification summarizing the month
    that just ended - income, expenses, and net savings.

    Reuses dashboard_service._get_summary_cards (an existing private
    helper) rather than re-deriving these aggregates - it's already exactly
    the income/expense/savings numbers this summary needs.
    """
    from backend.services import dashboard_service, alert_service
    from backend.services.notification_service import create_notification

    db = SessionLocal()
    try:
        today = date.today()
        # This job is meant to run on the 1st of the month, summarizing the
        # month that just ended. Stdlib-only date math (no python-dateutil
        # dependency) - the 1st of this month, minus one day, is always the
        # last day of the previous month.
        last_month_end = today.replace(day=1) - timedelta(days=1)
        first_day = last_month_end.replace(day=1)

        users = db.query(User).filter(User.is_verified.is_(True)).all()
        sent = 0

        for user in users:
            summary = dashboard_service._get_summary_cards(db, user.user_id, first_day, last_month_end)
            month_label = first_day.strftime("%B %Y")

            create_notification(
                db=db,
                user_id=user.user_id,
                title=f"Your {month_label} summary is ready",
                message=(
                    f"In {month_label}, you earned ₹{summary['total_income']:,.2f}, "
                    f"spent ₹{summary['total_expenses']:,.2f}, and saved "
                    f"₹{summary['total_savings']:,.2f}."
                ),
                action_url="/dashboard",
                type="system",
            )
            sent += 1

        logger.info("send_monthly_summaries: sent %d summaries for %s", sent, first_day.strftime("%B %Y"))
    except Exception:
        logger.exception("send_monthly_summaries job failed")
        db.rollback()
    finally:
        db.close()


def check_goal_deadlines() -> None:
    """
    Daily job: re-checks every active (non-completed) goal's status purely
    against today's date - a goal can flip on_track -> at_risk just from
    the calendar advancing past the 30-day mark, with no funding change at
    all, so this can't rely on the event hooks in goal_service alone.
    """
    from backend.models.goal import Goal
    from backend.services import goal_service, alert_service

    db = SessionLocal()
    try:
        goals = db.query(Goal).filter(Goal.status != "completed").all()
        flips = 0

        for goal in goals:
            old_status = goal.status
            goal.status = goal_service._compute_status(goal)
            if old_status != goal.status:
                flips += 1
                alert_service.check_goal_status_change(
                    db=db,
                    user_id=goal.user_id,
                    goal_name=goal.goal_name,
                    old_status=old_status,
                    new_status=goal.status,
                )

        db.commit()
        logger.info("check_goal_deadlines: %d goals flipped status", flips)
    except Exception:
        logger.exception("check_goal_deadlines job failed")
        db.rollback()
    finally:
        db.close()
