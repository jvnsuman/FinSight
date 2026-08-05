"""
Transaction services - CRUD logic + keep the linked account's balance in sync.
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models.transaction import Transaction
from backend.models.account import Account
from backend.schemas.transaction import TransactionCreate, TransactionUpdate

# payment_mode value the frontend sends for an ATM cash withdrawal. When a
# "transfer" transaction is logged with this payment_mode, the withdrawn
# amount is also credited into the user's default Cash Amount wallet, so the
# cash actually shows up somewhere instead of just vanishing from the source
# account.
ATM_WITHDRAWAL_PAYMENT_MODE = "ATM Withdrawal"


def _signed_amount(transaction_type: str, amount) -> Decimal:
    """Income increases balance, expense/transfer-out decreases it. Always normalizes to decimal."""
    amount=Decimal(str(amount))
    return amount if  transaction_type == "income" else -amount


def _apply_atm_withdrawal_credit(db: Session, user_id: int, source_account: Account, amount) -> None:
    """
    Credits the withdrawn cash into the user's default Cash Amount wallet.
    No-ops if the withdrawal was made *from* the cash wallet itself (nothing
    to move) or if the user somehow has no default wallet yet.
    """
    from backend.services.account_service import get_default_cash_account

    cash_account = get_default_cash_account(db, user_id)
    if not cash_account or cash_account.account_id == source_account.account_id:
        return
    cash_account.balance = (cash_account.balance or 0) + Decimal(str(amount))

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

    # ATM cash withdrawal: the amount leaving the source account should land
    # in the Cash Amount wallet rather than disappearing.
    if data.transaction_type == "transfer" and data.payment_mode == ATM_WITHDRAWAL_PAYMENT_MODE:
        _apply_atm_withdrawal_credit(db, user_id, account, data.amount)

    db.commit()
    db.refresh(transaction)

    # Overspend check: if this is an expense larger than what's currently free
    # in the savings pool, cover as much as possible from the pool and
    # surface the remaining shortfall as a warning rather than silently
    # pulling from a goal - the user chooses which goal(s) to draw the rest
    # from via a separate endpoint (see goals router: cover-shortfall).
    if data.transaction_type == "expense":
        transaction.savings_warning = _check_and_apply_savings_shortfall(
            db, user_id, Decimal(str(data.amount)), data.transaction_date
        )

    return transaction


def _check_and_apply_savings_shortfall(db: Session, user_id: int, expense_amount: Decimal, transaction_date):
    """
    Returns a SavingsShortfallWarning-shaped dict if this expense exceeds the
    user's available savings, after deducting what it can from the pool.
    Returns None if available savings comfortably covers the expense (the
    normal case) or if ensure_monthly_refill can't run for some reason.

    "Available savings" is savings_pool PLUS this calendar month's
    income-minus-expenses so far (excluding this expense, since it's
    deducted separately below) - not just savings_pool alone. savings_pool
    only gets topped up once per month via ensure_monthly_refill, so relying
    on it by itself would flag a shortfall for anyone who's saving normally
    this month but hasn't hit next month's refill yet.
    """
    # Local imports: transaction_service must not import goal_service/
    # savings_service/dashboard_service at module load time, since none of
    # those need transaction_service and it would risk a circular import later.
    from backend.services import savings_service
    from backend.services.dashboard_service import _get_summary_cards, _month_bounds

    try:
        user = savings_service.ensure_monthly_refill(db, user_id)
    except ValueError:
        return None

    first_day, last_day = _month_bounds(transaction_date.replace(day=1))
    summary = _get_summary_cards(db, user_id, first_day, last_day)
    # This expense was already committed to the DB by the time this runs
    # (see create_transaction), so total_expenses already includes it -
    # back it out to get "saved so far this month, before this expense".
    month_to_date_savings = max(
        Decimal(str(summary["total_income"])) - Decimal(str(summary["total_expenses"])) + expense_amount,
        Decimal("0"),
    )

    pool_before = Decimal(user.savings_pool)
    available_savings = pool_before + month_to_date_savings
    if expense_amount <= available_savings:
        return None  # comfortably covered - the normal, silent case

    # Draw from the pool first, then from this month's not-yet-swept savings.
    # Only the pool is an actual stored balance we adjust here - month-to-date
    # savings isn't sitting in a field we can zero out, it's just this
    # month's running income-minus-expenses, so there's nothing to deduct
    # from for that portion.
    amount_covered = available_savings
    remaining_shortfall = expense_amount - available_savings
    if pool_before > 0:
        user.savings_pool = Decimal("0")
        db.commit()

    return {
        "message": (
            f"This expense exceeded your available savings. "
            f"{float(amount_covered):.2f} was covered from your savings pool and this month's "
            f"savings so far, both of which are now used up. The remaining {float(remaining_shortfall):.2f} "
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

def _is_atm_withdrawal(transaction: Transaction) -> bool:
    return transaction.transaction_type == "transfer" and transaction.payment_mode == ATM_WITHDRAWAL_PAYMENT_MODE


def  update_transaction(db: Session, user_id: int, transaction_id: int, updates: TransactionUpdate) -> Transaction:
    transaction = get_transaction_or_404(db, user_id, transaction_id)
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()

    # Reverse the old amount's effect on the balance between applying the new one
    if account:
        account.balance = (account.balance or 0) - _signed_amount(transaction.transaction_type, transaction.amount)
        if _is_atm_withdrawal(transaction):
            _apply_atm_withdrawal_credit(db, user_id, account, -Decimal(str(transaction.amount)))

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    if account:
        account.balance = (account.balance or 0) + _signed_amount(transaction.transaction_type, transaction.amount)
        if _is_atm_withdrawal(transaction):
            _apply_atm_withdrawal_credit(db, user_id, account, transaction.amount)

    
    db.commit()
    db.refresh(transaction)
    return transaction

def delete_transaction(db: Session, user_id: int, transaction_id: int) -> None:
    transaction = get_transaction_or_404(db, user_id, transaction_id)
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()

    if account:
        account.balance = (account.balance or 0) - _signed_amount(transaction.transaction_type, transaction.amount)
        if _is_atm_withdrawal(transaction):
            _apply_atm_withdrawal_credit(db, user_id, account, -Decimal(str(transaction.amount)))

    db.delete(transaction)
    db.commit()