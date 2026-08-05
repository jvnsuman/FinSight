"""
API routers for managing user accounts(bank/card/wallet).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from backend.services.account_service import (
    create_account,
    get_user_accounts,
    get_account_or_404,
    update_account,
    delete_account,
    ensure_default_cash_account,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def add_account(
    data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new bank account, card, or wallet."""
    return create_account(db, current_user.user_id, data)


@router.get("", response_model=list[AccountResponse])
def list_accounts(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all accounts for the current user."""
    # Backfills the Cash Amount wallet for users who registered before this
    # feature existed - no-ops for everyone else since it's a lookup first.
    ensure_default_cash_account(db, current_user.user_id)
    return get_user_accounts(db, current_user.user_id, include_inactive)


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_account_or_404(db, current_user.user_id, account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{account_id}", response_model=AccountResponse)
def edit_account(
    account_id: int,
    updates: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_account(db, current_user.user_id, account_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-deletes the account (marks inactive) - transaction history is preserved."""
    try:
        delete_account(db, current_user.user_id, account_id)
    except ValueError as e:
        if str(e) == "Account not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
