"""
Budget Monitoring
Budget service - CRUD logic + computes spending utilization from real transactions.

Utilization is never stored - it's calculated fresh every time a budget is read,
by summing matching expense transactions for that month. This guarantees the
numbers are always accurate even if transactions are added/edited/deleted later.
"""

import calendar
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.account import Account
from backend.models.budget import Budget
from backend.models.category import Category
from backend.models.transaction import Transaction
from backend.models.user import User
from backend.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetConfirmationRequired(Exception):
    """
    Raised when a budget amount falls in Tier 3 (exceeds income + savings) and
    the caller hasn't set confirm_override=True yet. The router turns this into
    a 409 response carrying the warning details so the frontend can show a
    confirmation prompt and resubmit with confirm_override=True.
    """
    def __init__(self, message: str, income: Decimal, available_savings: Decimal, shortfall: Decimal):
        self.message = message
        self.income = income
        self.available_savings = available_savings
        self.shortfall = shortfall
        super().__init__(message)


def _month_bounds(month: date) -> tuple[date, date]:
    """Given any date, return (first_day, last_day) of that month."""
    first_day = month.replace(day=1)
    last_day = month.replace(day=calendar.monthrange(month.year, month.month)[1])
    return first_day, last_day


def _calculate_spent_amount(db: Session, user_id: int, category_id: int | None, month: date) -> Decimal:
    """
    Sum all 'expense' transactions for the user in the given month.
    If category_id is set, scoped to that category only.
    If category_id is None, sums ALL expense transactions that month (overall budget).
    """
    first_day, last_day = _month_bounds(month)

    query = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= first_day,
        Transaction.transaction_date <= last_day,
    )
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    result = query.scalar()
    return Decimal(str(result)) if result is not None else Decimal("0")


def _build_budget_response_data(db: Session, budget: Budget, income_warning: str | None = None) -> dict:
    """Attach computed utilization fields to a Budget row for the response schema."""
    spent = _calculate_spent_amount(db, budget.user_id, budget.category_id, budget.month)
    amount = Decimal(str(budget.amount))
    remaining = amount - spent
    utilization_percent = float((spent / amount) * 100) if amount > 0 else 0.0

    category_name = None
    if budget.category_id is not None:
        category = db.query(Category).filter(Category.category_id == budget.category_id).first()
        category_name = category.category_name if category else None

    return {
        "budget_id": budget.budget_id,
        "category_id": budget.category_id,
        "category_name": category_name,
        "amount": float(amount),
        "month": budget.month,
        "spent_amount": float(spent),
        "remaining_amount": float(remaining),
        "utilization_percent": round(utilization_percent, 2),
        "is_exceeded": spent > amount,
        "income_warning": income_warning,
    }


def _get_available_savings(db: Session, user_id: int) -> Decimal:
    """Sum of balances across the user's active accounts."""
    result = (
        db.query(func.coalesce(func.sum(Account.balance), 0))
        .filter(Account.user_id == user_id, Account.is_active.is_(True))
        .scalar()
    )
    return Decimal(str(result)) if result is not None else Decimal("0")


def _evaluate_income_tier(
    db: Session, user_id: int, amount: float, confirm_override: bool
) -> Optional[str]:
    """
    Runs the 3-tier income/savings check for a proposed budget amount.

    Tier 1 - amount <= monthly_income: allowed silently, returns None.
    Tier 2 - amount <= monthly_income + available_savings: allowed, returns a
             soft note describing how much is drawn from savings.
    Tier 3 - amount > monthly_income + available_savings: blocked unless
             confirm_override is True; raises BudgetConfirmationRequired.

    Raises ValueError if the user hasn't set monthly_income yet - budgets can't
    be sanity-checked against income until that's set.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None or user.monthly_income is None:
        raise ValueError(
            "Set your monthly income in your profile before creating a budget, "
            "so we can check it against your budget amounts."
        )

    income = Decimal(str(user.monthly_income))
    amount_dec = Decimal(str(amount))

    if amount_dec <= income:
        return None

    available_savings = _get_available_savings(db, user_id)
    ceiling = income + available_savings

    if amount_dec <= ceiling:
        drawn_from_savings = amount_dec - income
        return f"This budget uses ₹{drawn_from_savings:.2f} from your savings."

    if not confirm_override:
        shortfall = amount_dec - ceiling
        raise BudgetConfirmationRequired(
            message=(
                f"This budget of ₹{amount_dec:.2f} exceeds your income (₹{income:.2f}) "
                f"and available savings (₹{available_savings:.2f}) by ₹{shortfall:.2f}. "
                "Are you sure?"
            ),
            income=income,
            available_savings=available_savings,
            shortfall=shortfall,
        )

    # confirm_override=True: proceed anyway, but still surface the note.
    return (
        f"This budget exceeds your income and available savings by "
        f"₹{(amount_dec - ceiling):.2f}, based on your confirmation."
    )


def create_budget(db: Session, user_id: int, data: BudgetCreate) -> dict:
    if data.category_id is not None:
        category = (
            db.query(Category)
            .filter(Category.category_id == data.category_id, Category.user_id == user_id)
            .first()
        )
        if not category:
            raise ValueError("Category not found")

    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.category_id == data.category_id,
            Budget.month == data.month,
        )
        .first()
    )
    if existing:
        scope = "overall" if data.category_id is None else "this category"
        raise ValueError(f"A budget for {scope} already exists for this month")

    # Run the income/savings check last: it's the only check that can require
    # the caller to resubmit with confirm_override, so it shouldn't fire until
    # we know the budget is otherwise valid to create.
    warning = _evaluate_income_tier(db, user_id, data.amount, data.confirm_override)

    budget = Budget(
        user_id=user_id,
        category_id=data.category_id,
        amount=data.amount,
        month=data.month,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _build_budget_response_data(db, budget, income_warning=warning)


def get_user_budgets(db: Session, user_id: int, month: date | None = None) -> list[dict]:
    query = db.query(Budget).filter(Budget.user_id == user_id)
    if month is not None:
        query = query.filter(Budget.month == month.replace(day=1))

    budgets = query.order_by(Budget.month.desc(), Budget.category_id).all()
    return [_build_budget_response_data(db, b) for b in budgets]


def get_budget_or_404(db: Session, user_id: int, budget_id: int) -> Budget:
    budget = (
        db.query(Budget)
        .filter(Budget.budget_id == budget_id, Budget.user_id == user_id)
        .first()
    )
    if not budget:
        raise ValueError("Budget not found")
    return budget


def get_budget_detail(db: Session, user_id: int, budget_id: int) -> dict:
    budget = get_budget_or_404(db, user_id, budget_id)
    data = _build_budget_response_data(db, budget)
    data["transactions"] = _get_budget_transactions(db, user_id, budget.category_id, budget.month)
    return data


def _get_budget_transactions(db: Session, user_id: int, category_id: int | None, month: date) -> list[Transaction]:
    """
    Returns the expense transactions that make up a budget's spent_amount -
    same filter logic as _calculate_spent_amount, but returning the rows
    themselves rather than a sum, for the budget detail breakdown popup.
    """
    first_day, last_day = _month_bounds(month)

    query = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= first_day,
        Transaction.transaction_date <= last_day,
    )
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    return query.order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc()).all()


def update_budget(db: Session, user_id: int, budget_id: int, updates: BudgetUpdate) -> dict:
    budget = get_budget_or_404(db, user_id, budget_id)
    update_data = updates.model_dump(exclude_unset=True)
    update_data.pop("confirm_override", None)  # not a Budget column, used only for the check below

    warning = None
    if "amount" in update_data and update_data["amount"] is not None:
        warning = _evaluate_income_tier(db, user_id, update_data["amount"], updates.confirm_override)

    for field, value in update_data.items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return _build_budget_response_data(db, budget, income_warning=warning)


def delete_budget(db: Session, user_id: int, budget_id: int) -> None:
    budget = get_budget_or_404(db, user_id, budget_id)
    db.delete(budget)
    db.commit()

def get_locked_budget_amount(db: Session, user_id: int, month: date) -> Decimal:
    """
    Calculate funds locked by budgets (unspent budgeted amount) for a given month.
    Returns the maximum of (Overall Budget Remaining) vs (Sum of Category Budgets Remaining)
    to avoid double counting when both exist.
    """
    budgets = get_user_budgets(db, user_id, month)
    overall_remaining = Decimal("0")
    category_remaining_sum = Decimal("0")

    for b in budgets:
        rem = Decimal(str(b["remaining_amount"]))
        if rem > 0:
            if b["category_id"] is None:
                overall_remaining = rem
            else:
                category_remaining_sum += rem

    return max(overall_remaining, category_remaining_sum)
