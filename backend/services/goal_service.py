"""
Goal service - CRUD and progress/projection calculations for financial goals.

Status logic (kept simple and explainable, not a black box):
  - "completed"  : current_amount >= target_amount
  - "at_risk"    : not completed, and the monthly saving required to hit the
                   target by target_date is unrealistically high relative to
                   time remaining (specifically: less than 1 month remains
                   and the goal isn't complete)
  - "on_track"   : everything else

This is intentionally conservative/simple for Milestone 2. A more accurate
"at_risk" signal would compare required_monthly_saving against the user's
actual monthly income/savings rate (available once Milestone 1's budget data
is cross-referenced) - worth revisiting once that integration is wanted.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.models.goal import Goal
from backend.schemas.goal import GoalCreate, GoalUpdate


def _compute_derived_fields(goal: Goal) -> Goal:
    """Attaches progress_pct, amount_remaining, days_remaining, required_monthly_saving
    as transient attributes so they flow through GoalResponse without extra DB columns."""
    target = float(goal.target_amount)
    current = float(goal.current_amount)

    goal.progress_pct = min((current / target * 100) if target > 0 else 0, 100)
    goal.amount_remaining = max(target - current, 0)

    days_remaining = (goal.target_date - date.today()).days
    goal.days_remaining = days_remaining

    if days_remaining > 0 and goal.amount_remaining > 0:
        months_remaining = max(days_remaining / 30.44, 1 / 30.44)  # avoid div-by-zero for same-day targets
        goal.required_monthly_saving = goal.amount_remaining / months_remaining
    else:
        goal.required_monthly_saving = None

    return goal


def _compute_status(goal: Goal) -> str:
    if float(goal.current_amount) >= float(goal.target_amount):
        return "completed"
    days_remaining = (goal.target_date - date.today()).days
    if days_remaining <= 30 and float(goal.current_amount) < float(goal.target_amount):
        return "at_risk"
    return "on_track"


def create_goal(db: Session, user_id: int, data: GoalCreate) -> Goal:
    goal = Goal(
        user_id=user_id,
        goal_name=data.goal_name,
        goal_type=data.goal_type,
        target_amount=data.target_amount,
        current_amount=data.current_amount,
        target_date=data.target_date,
    )
    goal.status = _compute_status(goal)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _compute_derived_fields(goal)


def get_user_goals(db: Session, user_id: int) -> list[Goal]:
    goals = db.query(Goal).filter(Goal.user_id == user_id).order_by(Goal.target_date.asc()).all()
    # Refresh status on every read - a goal can flip from on_track to at_risk
    # purely by the calendar advancing, without any explicit update call.
    for goal in goals:
        goal.status = _compute_status(goal)
    db.commit()
    return [_compute_derived_fields(g) for g in goals]


def get_goal_or_404(db: Session, user_id: int, goal_id: int) -> Goal:
    goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise ValueError("Goal not found")
    goal.status = _compute_status(goal)
    db.commit()
    return _compute_derived_fields(goal)


def update_goal(db: Session, user_id: int, goal_id: int, updates: GoalUpdate) -> Goal:
    goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise ValueError("Goal not found")
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    goal.status = _compute_status(goal)
    db.commit()
    db.refresh(goal)
    return _compute_derived_fields(goal)


def delete_goal(db: Session, user_id: int, goal_id: int) -> None:
    """
    Hard-delete: unlike investments, a goal has no downstream "historical
    performance" view depending on it (Part 4's dashboard reads goals live,
    not from history), so there's no reason to keep a removed goal around.
    """
    goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise ValueError("Goal not found")
    db.delete(goal)
    db.commit()


def allocate_savings_to_goals(db: Session, user_id: int, source: str, percent: float) -> dict:
    """
    One-time manual allocation: takes `percent`% of the chosen source amount
    and distributes it across the user's active (not yet completed) goals,
    proportional to each goal's amount_remaining - a goal further from its
    target receives a larger share of the allocated total.

    If every active goal happens to be fully funded already (amount_remaining
    == 0 for all), there's nothing to weight by - falls back to an even split
    across those goals so the money isn't silently dropped.

    Raises ValueError if there are no active goals to allocate to, or if the
    source amount is not positive (nothing to allocate).

    IMPORTANT: this now actually deducts from the chosen source (fixed - it
    previously only grew goals without shrinking anything). 'wallet' deducts
    from User.cash_balance directly. 'income_savings' deducts from the
    persistent User.savings_pool (see savings_service), which is topped up
    monthly from income-expenses plus a wallet sweep - NOT the live, always-
    recalculated income-minus-expenses figure, since a live figure can't be
    drawn down permanently.
    """
    from backend.models.user import User
    from backend.services import savings_service

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found")

    if source == "wallet":
        source_amount = float(user.cash_balance)
    else:  # "income_savings" -> the persistent savings pool
        savings_service.ensure_monthly_refill(db, user_id)
        db.refresh(user)
        source_amount = float(user.savings_pool)

    if source_amount <= 0:
        raise ValueError(f"No positive balance available to allocate from source '{source}'.")

    goals = (
        db.query(Goal)
        .filter(Goal.user_id == user_id)
        .order_by(Goal.target_date.asc())
        .all()
    )
    for goal in goals:
        goal.status = _compute_status(goal)
    active_goals = [g for g in goals if g.status != "completed"]

    if not active_goals:
        raise ValueError("No active (incomplete) goals to allocate to.")

    total_to_allocate = source_amount * (percent / 100)

    remaining_amounts = [max(float(g.target_amount) - float(g.current_amount), 0) for g in active_goals]
    total_remaining = sum(remaining_amounts)

    if total_remaining > 0:
        weights = [r / total_remaining for r in remaining_amounts]
    else:
        # All active goals are (unexpectedly) at 0 remaining - split evenly
        # rather than divide by zero or silently allocate nothing.
        weights = [1 / len(active_goals)] * len(active_goals)

    allocation_lines = []
    for goal, weight in zip(active_goals, weights):
        amount = total_to_allocate * weight
        goal.current_amount = Decimal(str(goal.current_amount)) + Decimal(str(amount))
        goal.status = _compute_status(goal)
        allocation_lines.append({
            "goal_id": goal.goal_id,
            "goal_name": goal.goal_name,
            "amount_allocated": amount,
            "new_current_amount": float(goal.current_amount),
            "new_progress_pct": min((float(goal.current_amount) / float(goal.target_amount) * 100) if float(goal.target_amount) > 0 else 0, 100),
        })

    # Actually deduct from the source now that goals have been credited.
    if source == "wallet":
        user.cash_balance = Decimal(str(user.cash_balance)) - Decimal(str(total_to_allocate))
    else:
        user.savings_pool = Decimal(str(user.savings_pool)) - Decimal(str(total_to_allocate))

    db.commit()

    return {
        "source": source,
        "source_amount": source_amount,
        "percent_applied": percent,
        "total_allocated": total_to_allocate,
        "allocations": allocation_lines,
    }


def cover_shortfall_from_goals(db: Session, user_id: int, withdrawals: list[dict]) -> dict:
    """
    Withdraws a user-specified amount from each of the user-specified goals
    (following an overspend warning from transaction_service). Unlike
    allocate_savings_to_goals, this is a manual, per-goal, user-directed
    action - the user already saw exactly which goal(s) they're pulling from
    and how much, so there's no proportional-split logic here.

    Raises ValueError if a goal_id doesn't belong to this user, or if a
    withdrawal amount exceeds that goal's current_amount (can't withdraw
    more than the goal actually holds).
    """
    updated_lines = []
    total_withdrawn = Decimal("0")

    for withdrawal in withdrawals:
        goal = (
            db.query(Goal)
            .filter(Goal.goal_id == withdrawal["goal_id"], Goal.user_id == user_id)
            .first()
        )
        if not goal:
            raise ValueError(f"Goal {withdrawal['goal_id']} not found")

        amount = Decimal(str(withdrawal["amount"]))
        if amount > Decimal(goal.current_amount):
            raise ValueError(
                f"Cannot withdraw {float(amount):.2f} from '{goal.goal_name}' - "
                f"it only holds {float(goal.current_amount):.2f}."
            )

        goal.current_amount = Decimal(goal.current_amount) - amount
        goal.status = _compute_status(goal)
        total_withdrawn += amount

        updated_lines.append({
            "goal_id": goal.goal_id,
            "goal_name": goal.goal_name,
            "amount_allocated": float(-amount),  # negative - this is a withdrawal, reusing the same line shape
            "new_current_amount": float(goal.current_amount),
            "new_progress_pct": min((float(goal.current_amount) / float(goal.target_amount) * 100) if float(goal.target_amount) > 0 else 0, 100),
        })

    db.commit()

    return {
        "total_withdrawn": float(total_withdrawn),
        "updated_goals": updated_lines,
    }


def fund_specific_goal(db: Session, user_id: int, goal_id: int, source: str, amount: float = None, percent: float = None) -> dict:
    """
    Funds exactly ONE goal, chosen by the user, bypassing the proportional
    split used by allocate_savings_to_goals entirely. Either a fixed amount
    or a percent of the source is given (never both - enforced at the
    schema level via FundGoalRequest).

    Actually deducts from the chosen source, same as allocate_savings_to_goals:
    'wallet' -> User.cash_balance, 'income_savings' -> User.savings_pool (after
    ensuring the monthly refill has run).

    Raises ValueError if: the goal doesn't belong to this user, the goal is
    already completed, the source balance is not positive, or the requested
    amount (fixed or percent-derived) exceeds the available source balance.
    """
    from backend.models.user import User
    from backend.services import savings_service

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError("User not found")

    goal = db.query(Goal).filter(Goal.goal_id == goal_id, Goal.user_id == user_id).first()
    if not goal:
        raise ValueError("Goal not found")

    goal.status = _compute_status(goal)
    if goal.status == "completed":
        raise ValueError(f"'{goal.goal_name}' is already fully funded.")

    if source == "wallet":
        source_balance = Decimal(user.cash_balance)
    else:  # "income_savings" -> persistent savings pool
        savings_service.ensure_monthly_refill(db, user_id)
        db.refresh(user)
        source_balance = Decimal(user.savings_pool)

    if source_balance <= 0:
        raise ValueError(f"No positive balance available in source '{source}'.")

    if percent is not None:
        fund_amount = source_balance * (Decimal(str(percent)) / 100)
    else:
        fund_amount = Decimal(str(amount))
        if fund_amount > source_balance:
            raise ValueError(
                f"Cannot fund {float(fund_amount):.2f} - your {source} balance is only {float(source_balance):.2f}."
            )

    goal.current_amount = Decimal(goal.current_amount) + fund_amount
    goal.status = _compute_status(goal)

    if source == "wallet":
        user.cash_balance = source_balance - fund_amount
        remaining_balance = user.cash_balance
    else:
        user.savings_pool = source_balance - fund_amount
        remaining_balance = user.savings_pool

    db.commit()
    db.refresh(goal)

    return {
        "goal_id": goal.goal_id,
        "goal_name": goal.goal_name,
        "source": source,
        "amount_funded": float(fund_amount),
        "new_current_amount": float(goal.current_amount),
        "new_progress_pct": min((float(goal.current_amount) / float(goal.target_amount) * 100) if float(goal.target_amount) > 0 else 0, 100),
        "remaining_source_balance": float(remaining_balance),
    }
