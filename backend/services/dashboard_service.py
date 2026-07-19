"""
Financial Dashboard
Dashboard service - pulls together Accounts/Categories/Transactions (Part 2)
and Budgets (Part 3) into one combined summary. Nothing here is stored -
everything is calculated live from existing tables.
"""

import calendar
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.transaction import Transaction
from backend.models.category import Category
from backend.models.budget import Budget


def _month_bounds(month: date) -> tuple[date, date]:
    first_day = month.replace(day=1)
    last_day = month.replace(day=calendar.monthrange(month.year, month.month)[1])
    return first_day, last_day


def _get_summary_cards(db: Session, user_id: int, first_day: date, last_day: date) -> dict:
    income_total = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "income",
            Transaction.transaction_date >= first_day,
            Transaction.transaction_date <= last_day,
        )
        .scalar()
    )
    expense_total = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= first_day,
            Transaction.transaction_date <= last_day,
        )
        .scalar()
    )

    income_total = Decimal(str(income_total))
    expense_total = Decimal(str(expense_total))
    savings = income_total - expense_total

    # Overall (non-category) budget for this month, if one exists
    overall_budget = (
        db.query(Budget)
        .filter(Budget.user_id == user_id, Budget.category_id.is_(None), Budget.month == first_day)
        .first()
    )
    if overall_budget and Decimal(str(overall_budget.amount)) > 0:
        utilization = float((expense_total / Decimal(str(overall_budget.amount))) * 100)
    else:
        utilization = 0.0

    return {
        "total_income": float(income_total),
        "total_expenses": float(expense_total),
        "total_savings": float(savings),
        "budget_utilization_percent": round(utilization, 2),
    }


def _get_expense_breakdown(db: Session, user_id: int, first_day: date, last_day: date) -> list[dict]:
    rows = (
        db.query(
            Transaction.category_id,
            Category.category_name,
            func.sum(Transaction.amount).label("total"),
        )
        .outerjoin(Category, Transaction.category_id == Category.category_id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= first_day,
            Transaction.transaction_date <= last_day,
        )
        .group_by(Transaction.category_id, Category.category_name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    grand_total = sum(Decimal(str(r.total)) for r in rows) or Decimal("1")  # avoid div-by-zero

    breakdown = []
    for r in rows:
        amount = Decimal(str(r.total))
        breakdown.append({
            "category_id": r.category_id,
            "category_name": r.category_name or "Uncategorized",
            "amount": float(amount),
            "percent_of_total": round(float((amount / grand_total) * 100), 2),
        })
    return breakdown


def _get_monthly_trend(db: Session, user_id: int, first_day: date, last_day: date) -> list[dict]:
    rows = (
        db.query(
            Transaction.transaction_date,
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type.in_(["income", "expense"]),
            Transaction.transaction_date >= first_day,
            Transaction.transaction_date <= last_day,
        )
        .group_by(Transaction.transaction_date, Transaction.transaction_type)
        .order_by(Transaction.transaction_date)
        .all()
    )

    by_date: dict = {}
    for r in rows:
        entry = by_date.setdefault(r.transaction_date, {"income": 0.0, "expenses": 0.0})
        if r.transaction_type == "income":
            entry["income"] = float(r.total)
        else:
            entry["expenses"] = float(r.total)

    return [
        {"date": d, "income": v["income"], "expenses": v["expenses"]}
        for d, v in sorted(by_date.items())
    ]


def _get_recent_transactions(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    rows = (
        db.query(Transaction)
        .outerjoin(Category, Transaction.category_id == Category.category_id)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
        .limit(limit)
        .all()
    )

    results = []
    for t in rows:
        results.append({
            "transaction_id": t.transaction_id,
            "transaction_type": t.transaction_type,
            "amount": float(t.amount),
            "description": t.description,
            "category_name": t.category.category_name if t.category else None,
            "payment_mode": t.payment_mode,
            "transaction_date": t.transaction_date,
        })
    return results


def get_dashboard_summary(db: Session, user_id: int, month: date) -> dict:
    """
    Build the full dashboard payload for a given month.
    `month` can be any date within the target month - normalized to the 1st internally.
    """
    first_day, last_day = _month_bounds(month.replace(day=1))

    return {
        "month": first_day,
        "summary": _get_summary_cards(db, user_id, first_day, last_day),
        "expense_breakdown": _get_expense_breakdown(db, user_id, first_day, last_day),
        "monthly_trend": _get_monthly_trend(db, user_id, first_day, last_day),
        "recent_transactions": _get_recent_transactions(db, user_id),
    }
