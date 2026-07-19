"""Financial Dashboard
Single combined endpoint that aggregates Accounts/Categories/Transactions (Part 2)
and Budgets (Part 3) into the dashboard view.
"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.dashboard import DashboardResponse
from backend.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardResponse)
def dashboard_summary(
    month: date | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns everything needed to render the dashboard in one call:
    - summary cards (income, expenses, savings, budget utilization)
    - expense breakdown by category (for the pie chart)
    - daily income/expense trend (for the line chart)
    - 5 most recent transactions

    Defaults to the current calendar month if `month` isn't provided.
    Pass any date within the target month, e.g. ?month=2026-07-01
    """
    target_month = month or date.today()
    return get_dashboard_summary(db, current_user.user_id, target_month)
