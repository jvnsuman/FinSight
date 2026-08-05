"""
Account service - CRUD logic user account (bank/card/wallet).
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from backend.models.account import Account
from backend.schemas.account import AccountCreate, AccountUpdate

# Name of the system-seeded cash wallet every user gets on registration.
# ATM withdrawals are credited to whichever of the user's accounts has
# is_default=True, so this name is only used at creation time - lookups
# elsewhere should filter on is_default, not on this string.
CASH_ACCOUNT_NAME = "Cash Amount"


def ensure_default_cash_account(db: Session, user_id: int) -> Account:
    """
    Create the user's default "Cash Amount" wallet if they don't already have
    one. Called once, right after registration succeeds (mirrors
    seed_default_categories in category_service) - safe to call again since
    it no-ops if a default account already exists.
    """
    existing = (
        db.query(Account)
        .filter(Account.user_id == user_id, Account.is_default.is_(True))
        .first()
    )
    if existing:
        return existing

    account = Account(
        user_id=user_id,
        account_name=CASH_ACCOUNT_NAME,
        account_type="wallet",
        balance=0,
        is_default=True,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_default_cash_account(db: Session, user_id: int) -> Account | None:
    """Returns the user's system-seeded Cash Amount wallet, if it exists."""
    return (
        db.query(Account)
        .filter(Account.user_id == user_id, Account.is_default.is_(True))
        .first()
    )


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

    The system-seeded Cash Amount wallet can't be deleted - ATM withdrawals
    and other cash flows depend on always having exactly one default account
    to credit.
    """
    account = get_account_or_404(db, user_id, account_id)
    if account.is_default:
        raise ValueError("The Cash Amount account can't be deleted.")
    account.is_active = False
    db.commit()
