
"""
Budget Monitoring
API routes for creating and tracking budgets (per-category or overall).
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from backend.services.budget_service import (
    create_budget,
    get_user_budgets,
    get_budget_detail,
    update_budget,
    delete_budget,
    BudgetConfirmationRequired,
)

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def add_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a budget for a month. Leave category_id null for an overall total
    budget covering all spending; set it for a category-specific limit.
    Only one budget per category (or one overall) is allowed per month.

    The amount is checked against the user's monthly income and available
    savings (sum of active account balances):
      - Tier 1 (<= income): created silently.
      - Tier 2 (<= income + savings): created, with `income_warning` noting
        how much is drawn from savings.
      - Tier 3 (> income + savings): rejected with 409 and a warning message
        unless `confirm_override: true` is sent, in which case it's created
        with an `income_warning` explaining the shortfall.

    Requires the user's profile to have `monthly_income` set - returns 400
    otherwise.
    """
    try:
        return create_budget(db, current_user.user_id, data)
    except BudgetConfirmationRequired as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": e.message,
                "income": float(e.income),
                "available_savings": float(e.available_savings),
                "shortfall": float(e.shortfall),
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    month: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all budgets for the current user, with live utilization calculated
    from actual transactions. Optionally filter to a specific month.
    """
    return get_user_budgets(db, current_user.user_id, month)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_budget_detail(db, current_user.user_id, budget_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{budget_id}", response_model=BudgetResponse)
def edit_budget(
    budget_id: int,
    updates: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a budget's amount. Category and month cannot be changed - delete and
    recreate instead. The same income/savings tier check as budget creation
    applies whenever `amount` is included in the update.
    """
    try:
        return update_budget(db, current_user.user_id, budget_id, updates)
    except BudgetConfirmationRequired as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": e.message,
                "income": float(e.income),
                "available_savings": float(e.available_savings),
                "shortfall": float(e.shortfall),
            },
        )
    except ValueError as e:
        # "Budget not found" -> 404; the income-not-set message -> 400.
        if str(e) == "Budget not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        delete_budget(db, current_user.user_id, budget_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
