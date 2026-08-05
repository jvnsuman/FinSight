"""
Milestone 3 - Financial Alert Triggers

This is the logic layer that decides WHEN to actually call
notification_service.create_notification() for budget, goal, and investment
events. It's kept separate from budget_service/goal_service/trade_service
themselves so those files stay focused on their own CRUD/calculation logic;
this file is imported INTO them (following the same local-import convention
already used in transaction_service.py for savings_service, to avoid
circular imports).

CROSSING DETECTION - why it matters:
Budget utilization and goal progress are computed fresh on almost every read
(see budget_service._calculate_spent_amount, goal_service._compute_status) -
they are not stored, so re-reading them is not itself an "event". If we
naively fired a notification every time utilization was calculated, a user
opening their Budgets page 10 times a day at 85% utilization would get 10
duplicate alerts.

Instead, every check function here takes both the OLD and NEW value and only
notifies when a threshold is newly crossed in this specific call. That means
these functions must be called right at the point of mutation (after a
transaction is created, after a goal is funded, after a trade executes) -
not from a generic "get" endpoint.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from backend.services.notification_service import create_notification

# Budget utilization thresholds, in ascending order. Kept as a private
# module-level constant (not a DB setting) since Milestone 3's scope doesn't
# call for per-user configurable thresholds.
BUDGET_THRESHOLDS = [50, 80, 100]

# Goal progress milestones, in ascending order.
GOAL_PROGRESS_MILESTONES = [25, 50, 75, 100]

# A holding's price needs to move at least this much in one day (vs its
# previous close) to be worth alerting on - keeps this from firing on noise.
INVESTMENT_DAILY_MOVE_THRESHOLD_PERCENT = Decimal("5")


def _highest_threshold_crossed(old_value: float, new_value: float, thresholds: list[int]) -> int | None:
    """
    Returns the highest threshold that `new_value` reaches or exceeds but
    `old_value` did not - i.e. the threshold that was JUST crossed by this
    change. Returns None if no new threshold was crossed (value went down,
    or stayed within the same band, or hasn't reached the lowest one yet).
    """
    crossed = [t for t in thresholds if old_value < t <= new_value]
    return max(crossed) if crossed else None


def check_budget_threshold(
    db: Session,
    user_id: int,
    budget_label: str,
    old_spent: Decimal,
    new_spent: Decimal,
    budget_amount: Decimal,
) -> None:
    """
    Call this right after a new expense transaction changes a budget's
    spent amount. Fires a notification if this transaction pushed
    utilization past 50%, 80%, or 100% for the first time this month.

    `budget_label` should already be a human-readable name, e.g.
    "Food & Dining" or "Overall Budget" - the caller resolves category
    names, this function doesn't need to know about categories.
    """
    if budget_amount <= 0:
        return  # a zero/negative budget has no meaningful utilization to cross

    old_pct = float(old_spent) / float(budget_amount) * 100
    new_pct = float(new_spent) / float(budget_amount) * 100

    threshold = _highest_threshold_crossed(old_pct, new_pct, BUDGET_THRESHOLDS)
    if threshold is None:
        return

    if threshold >= 100:
        title = f"{budget_label} budget exceeded"
        message = (
            f"You've spent {new_pct:.0f}% of your {budget_label} budget this month "
            f"(₹{float(new_spent):,.2f} of ₹{float(budget_amount):,.2f})."
        )
    else:
        title = f"{budget_label} budget at {threshold}%"
        message = (
            f"You've used {new_pct:.0f}% of your {budget_label} budget this month "
            f"(₹{float(new_spent):,.2f} of ₹{float(budget_amount):,.2f})."
        )

    create_notification(
        db=db, user_id=user_id, title=title, message=message, type="budget", action_url="/budgets"
    )


def check_goal_progress(
    db: Session,
    user_id: int,
    goal_name: str,
    old_progress_pct: float,
    new_progress_pct: float,
) -> None:
    """
    Call this right after a goal's current_amount changes (funding,
    withdrawal, or manual edit). Fires a notification if this change pushed
    progress past 25%, 50%, 75%, or 100% for the first time.
    """
    threshold = _highest_threshold_crossed(old_progress_pct, new_progress_pct, GOAL_PROGRESS_MILESTONES)
    if threshold is None:
        return

    if threshold >= 100:
        title = f"Goal achieved: {goal_name}"
        message = f"Congratulations! You've fully funded your '{goal_name}' goal."
    else:
        title = f"{goal_name}: {threshold}% funded"
        message = f"Your '{goal_name}' goal has reached {threshold}% of its target."

    create_notification(
        db=db, user_id=user_id, title=title, message=message, type="goal", action_url="/goals"
    )


def check_goal_status_change(
    db: Session,
    user_id: int,
    goal_name: str,
    old_status: str,
    new_status: str,
) -> None:
    """
    Call this after any goal status recomputation. Fires only on the
    specific transition INTO "at_risk" (not every time the goal is read
    while already at_risk) - the calendar advancing past the 30-day mark is
    itself the trigger even without a funding change, which is why this is
    a separate check from check_goal_progress rather than folded into it.
    """
    if old_status != "at_risk" and new_status == "at_risk":
        create_notification(
            db=db,
            user_id=user_id,
            title=f"Goal at risk: {goal_name}",
            message=(
                f"'{goal_name}' is at risk of missing its target date - "
                f"less than a month remains and it isn't fully funded yet."
            ),
            type="goal",
            action_url="/goals",
        )


def check_investment_price_move(
    db: Session,
    user_id: int,
    asset_name: str,
    current_price: Decimal,
    previous_close: Decimal,
) -> None:
    """
    Call this from the scheduled price-check job (see
    backend/scheduler/jobs.py) once per holding, per sweep. Fires when a
    holding moves at least INVESTMENT_DAILY_MOVE_THRESHOLD_PERCENT vs its
    previous close, in either direction.
    """
    if previous_close is None or previous_close == 0:
        return

    change_pct = (Decimal(current_price) - Decimal(previous_close)) / Decimal(previous_close) * 100
    if abs(change_pct) < INVESTMENT_DAILY_MOVE_THRESHOLD_PERCENT:
        return

    direction = "up" if change_pct > 0 else "down"
    create_notification(
        db=db,
        user_id=user_id,
        title=f"{asset_name} is {direction} {abs(change_pct):.1f}%",
        message=f"{asset_name} has moved {direction} {abs(change_pct):.1f}% since the previous close.",
        type="investment",
        action_url="/portfolio",
    )


def notify_trade_executed(db: Session, user_id: int, action: str, asset_name: str, quantity: Decimal, price: Decimal) -> None:
    """
    Call this right after a buy/sell trade commits. Unlike the threshold
    checks above, every trade fires exactly one notification - there's no
    "crossing" concept for a discrete action the user just took themselves,
    this is simply a confirmation.
    """
    verb = "Bought" if action == "buy" else "Sold"
    create_notification(
        db=db,
        user_id=user_id,
        title=f"{verb} {asset_name}",
        message=f"{verb} {float(quantity):g} units of {asset_name} at ₹{float(price):,.2f} each.",
        type="investment",
        action_url="/investments",
    )


# Financial health score bands, mirrored from
# financial_health_service._get_health_category. A user only needs to hear
# about it when their standing changes for the better or the worse - not on
# every routine cache refresh - so this only cares about two edges:
# entering "good" territory (score >= HEALTH_GOOD_THRESHOLD) and entering
# "bad" territory (score < HEALTH_BAD_THRESHOLD).
HEALTH_GOOD_THRESHOLD = 60   # "Good" or better, per _get_health_category
HEALTH_BAD_THRESHOLD = 40    # below this is "Financially At Risk"


def check_health_score_status(
    db: Session,
    user_id: int,
    old_score: int | None,
    new_score: int,
    category: str,
) -> None:
    """
    Call this right after the financial health score is recomputed. Fires a
    notification only when the score newly crosses into "good" territory
    (>= HEALTH_GOOD_THRESHOLD) or newly crosses into "bad" territory
    (< HEALTH_BAD_THRESHOLD), so the user is told when their standing
    actually changes rather than being re-notified every refresh while it
    stays in the same band. old_score=None (first-ever calculation) never
    fires, since there's nothing to compare against yet.
    """
    if old_score is None:
        return

    was_good = old_score >= HEALTH_GOOD_THRESHOLD
    is_good = new_score >= HEALTH_GOOD_THRESHOLD
    was_bad = old_score < HEALTH_BAD_THRESHOLD
    is_bad = new_score < HEALTH_BAD_THRESHOLD

    if is_good and not was_good:
        create_notification(
            db=db,
            user_id=user_id,
            title="Your financial health is looking good",
            message=(
                f"Your financial health score is now {new_score} ({category}). "
                f"Keep up the good habits that got you here."
            ),
            type="health_score",
            action_url="/financial-health",
        )
    elif is_bad and not was_bad:
        create_notification(
            db=db,
            user_id=user_id,
            title="Your financial health needs attention",
            message=(
                f"Your financial health score has dropped to {new_score} ({category}). "
                f"Take a look at what's pulling it down."
            ),
            type="health_score",
            action_url="/financial-health",
        )
