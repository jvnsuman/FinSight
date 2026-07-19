"""
Transaction services - CRUD logic + keep the linked account's balance in sync.
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models.transaction import Transaction
from backend.models.account import Account
from backend.schemas.transaction import TransactionCreate, TransactionUpdate


def _signed_amount(transaction_type: str, amount) -> Decimal:
    """Income increases balance, expense/transfer-out decreases it. Always normalizes to decimal."""
    amount=Decimal(str(amount))
    return amount if  transaction_type == "income" else -amount

def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    account = (
        db.query(Account)
        .filter(Account.account_id==data.account_id, Account.user_id == user_id)
        .first()
    )
    if not account:
        raise ValueError("Account not found")
    
    transaction = Transaction(
        user_id=user_id,
        account_id=data.account_id,
        category_id=data.category_id,
        transaction_type=data.transaction_type,
        amount=data.amount,
        description=data.description,
        payment_mode=data.payment_mode,
        transaction_date=data.transaction_date,
    )
    db.add(transaction)

    # keep the account balance in sync
    account.balance = (account.balance or 0) + _signed_amount(data.transaction_type, data.amount)

    db.commit()
    db.refresh(transaction)

    # Overspend check: if this is an expense larger than what's currently free
    # in the savings pool, cover as much as possible from the pool and
    # surface the remaining shortfall as a warning rather than silently
    # pulling from a goal - the user chooses which goal(s) to draw the rest
    # from via a separate endpoint (see goals router: cover-shortfall).
    if data.transaction_type == "expense":
        transaction.savings_warning = _check_and_apply_savings_shortfall(db, user_id, Decimal(str(data.amount)))

    return transaction


def _check_and_apply_savings_shortfall(db: Session, user_id: int, expense_amount: Decimal):
    """
    Returns a SavingsShortfallWarning-shaped dict if this expense exceeds the
    user's savings_pool, after deducting what it can from the pool. Returns
    None if the pool comfortably covers the expense (the normal case) or if
    ensure_monthly_refill can't run for some reason.
    """
    # Local imports: transaction_service must not import goal_service/
    # savings_service at module load time, since neither of those needs
    # transaction_service and it would risk a circular import later.
    from backend.services import savings_service

    try:
        user = savings_service.ensure_monthly_refill(db, user_id)
    except ValueError:
        return None

    pool_before = Decimal(user.savings_pool)
    if expense_amount <= pool_before:
        return None  # comfortably covered - the normal, silent case

    amount_covered = pool_before
    remaining_shortfall = expense_amount - pool_before
    user.savings_pool = Decimal("0")
    db.commit()

    return {
        "message": (
            f"This expense exceeded your available savings. "
            f"{float(amount_covered):.2f} was covered from your savings pool, "
            f"which has now run out. The remaining {float(remaining_shortfall):.2f} "
            f"is not yet covered - choose which goal(s) to draw it from."
        ),
        "savings_pool_before": float(pool_before),
        "amount_covered_by_savings": float(amount_covered),
        "remaining_shortfall": float(remaining_shortfall),
        "savings_pool_after": 0.0,
    }

def get_user_transactions(
        db: Session,
        user_id: int,
        account_id: int | None = None,
        category_id: int | None = None,
        transaction_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
) -> list[Transaction]:
    filters = [Transaction.user_id==user_id]
    if account_id is not None:
        filters.append(Transaction.account_id==account_id)
    if category_id is not None:
        filters.append(Transaction.category_id == category_id)
    if transaction_type is not None:
        filters.append(Transaction.transaction_type == transaction_type)
    
    return (
        db.query(Transaction)
        .filter(and_(*filters))
        .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_transaction_or_404(db: Session, user_id: int,transaction_id: int) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(Transaction.transaction_id==transaction_id, Transaction.user_id == user_id)
        .first()
    )
    if not transaction:
        raise ValueError("Transaction not found")
    return transaction

def  update_transaction(db: Session, user_id: int, transaction_id: int, updates: TransactionUpdate) -> Transaction:
    transaction = get_transaction_or_404(db, user_id, transaction_id)
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()

    # Reverse the old amount's effect on the balance between applying the new one
    if account:
        account.balance = (account.balance or 0) - _signed_amount(transaction.transaction_type, transaction.amount)

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    if account:
        account.balance = (account.balance or 0) + _signed_amount(transaction.transaction_type, transaction.amount)

    
    db.commit()
    db.refresh(transaction)
    return transaction

def delete_transaction(db: Session, user_id: int, transaction_id: int) -> None:
    transaction = get_transaction_or_404(db, user_id, transaction_id)
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()

    if account:
        account.balance = (account.balance or 0) - _signed_amount(transaction.transaction_type, transaction.amount)

    db.delete(transaction)
    db.commit()