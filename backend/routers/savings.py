"""
Savings pool endpoints - currently just the breakdown used by the "click the
Savings Pool card" popup on the dashboard. The pool total itself is already
exposed on GET /dashboard as savings_pool, so this router doesn't duplicate
a plain "get the current total" endpoint.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.savings import SavingsBreakdownResponse
from backend.services.savings_service import get_savings_breakdown

router = APIRouter(prefix="/savings", tags=["Savings"])


@router.get("/breakdown", response_model=SavingsBreakdownResponse)
def savings_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns what makes up the user's current savings pool total: this
    month's already-applied contribution, wallet cash still pending next
    month's sweep, and how much has already been allocated out to goals.
    """
    return get_savings_breakdown(db, current_user.user_id)
