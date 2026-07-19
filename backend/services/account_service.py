"""
Account service - CRUD logic user account (bank/card/wallet).
"""

from sqlalchemy.orm import Session

from backend.models.account import Account
from backend.schemas.account import AccountCreate, AccountUpdate

def create_account(db: Session, user_id: int, data: AccountCreate) -> Account:
    account = Account(
        user_id=user_id,
        account_name=data.account_name,
        account_type=data.account_type,
        bank_name=data.bank_name,
        account_number=data.account_number,
        balance=data.balance,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_user_accounts(db: Session, user_id: int, include_inactive: bool = False) -> list[Account]:
    query = db.query(Account).filter(Account.user_id == user_id)
    if not include_inactive:
        query = query.filter(Account.is_active.is_(True))
    return query.order_by(Account.created_at).all()


def get_account_or_404(db: Session, user_id: int, account_id: int) -> Account:
    account = (
        db.query(Account)
        .filter(Account.account_id == account_id, Account.user_id == user_id)
        .first()
    )
    if not account:
        raise ValueError("Account not found")
    return account


def update_account(db: Session, user_id: int, account_id: int, updates: AccountUpdate) -> Account:
    account = get_account_or_404(db, user_id, account_id)
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, user_id: int, account_id: int) -> None:
    """
    Soft-delete: marks the account inactive rather than removing it,
    so historical transactions linked to it remain intact.
    """
    account = get_account_or_404(db, user_id, account_id)
    account.is_active = False
    db.commit()
