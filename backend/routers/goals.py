"""
API routers for managing financial goals (savings targets with progress tracking).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse,
    AllocateSavingsRequest, AllocateSavingsResponse,
    CoverShortfallRequest, CoverShortfallResponse,
    FundGoalRequest, FundGoalResponse,
)
from backend.services.goal_service import (
    create_goal,
    get_user_goals,
    get_goal_or_404,
    update_goal,
    delete_goal,
    allocate_savings_to_goals,
    cover_shortfall_from_goals,
    fund_specific_goal,
)

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def add_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new financial goal."""
    return create_goal(db, current_user.user_id, data)


@router.get("", response_model=list[GoalResponse])
def list_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all goals for the current user, ordered by nearest target date first."""
    return get_user_goals(db, current_user.user_id)


# NOTE: must be declared before "/{goal_id}" - otherwise FastAPI would try to
# parse "allocate-savings" as a goal_id and 422 on every call.
@router.post("/allocate-savings", response_model=AllocateSavingsResponse)
def allocate_savings(
    data: AllocateSavingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    One-time manual allocation: distributes `percent`% of the chosen savings
    source across all active (incomplete) goals, weighted by how much each
    goal still needs (a goal further from its target gets a bigger share).
    """
    try:
        return allocate_savings_to_goals(db, current_user.user_id, data.source, data.percent)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# NOTE: must also be declared before "/{goal_id}" for the same reason as
# allocate-savings above.
@router.post("/cover-shortfall", response_model=CoverShortfallResponse)
def cover_shortfall(
    data: CoverShortfallRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Follows up on a savings_warning returned from creating an expense
    transaction: the user picks which goal(s) to withdraw the uncovered
    shortfall from, and how much from each.
    """
    try:
        withdrawals = [w.model_dump() for w in data.withdrawals]
        return cover_shortfall_from_goals(db, current_user.user_id, withdrawals)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_goal_or_404(db, current_user.user_id, goal_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{goal_id}/fund", response_model=FundGoalResponse)
def fund_goal(
    goal_id: int,
    data: FundGoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Funds exactly this one goal with a fixed amount or a percent of the
    chosen source - bypassing the proportional split used by
    /goals/allocate-savings entirely. Actually deducts from the source.
    """
    try:
        return fund_specific_goal(
            db, current_user.user_id, goal_id,
            source=data.source, amount=data.amount, percent=data.percent,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{goal_id}", response_model=GoalResponse)
def edit_goal(
    goal_id: int,
    updates: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_goal(db, current_user.user_id, goal_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        delete_goal(db, current_user.user_id, goal_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
