"""
API routers for the simulated trading wallet: deposit cash, buy/sell holdings,
view trade history. All simulated - no real money moves.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.trade import WalletResponse, DepositRequest, BuyRequest, SellRequest, TradeResponse
from backend.services.trade_service import (
    TradeError,
    get_wallet,
    deposit,
    execute_buy,
    execute_sell,
    get_trade_history,
)
from backend.services import savings_service

router = APIRouter(prefix="/trading", tags=["Trading"])


@router.get("/wallet", response_model=WalletResponse)
def wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Reading the wallet is also the (lazy) trigger point for the monthly
    # savings refill - see savings_service.ensure_monthly_refill.
    savings_pool = savings_service.get_savings_pool(db, current_user.user_id)
    return {
        "cash_balance": float(get_wallet(db, current_user.user_id)),
        "savings_pool": float(savings_pool),
    }


@router.post("/deposit", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def add_funds(
    data: DepositRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds simulated cash to the user's wallet. No real payment is processed."""
    try:
        return deposit(db, current_user.user_id, data.amount)
    except TradeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/buy", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def buy(
    data: BuyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Simulated buy. Deducts quantity * price from the wallet and adds to (or
    averages into) the matching holding. Fails with 400 if funds are
    insufficient or no price can be resolved.
    """
    try:
        return execute_buy(db, current_user.user_id, data)
    except TradeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sell", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
def sell(
    data: SellRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Simulated sell. Reduces the holding's quantity and credits proceeds to
    the wallet. Selling the full quantity soft-deletes the holding.
    """
    try:
        return execute_sell(db, current_user.user_id, data)
    except TradeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history", response_model=list[TradeResponse])
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trades = get_trade_history(db, current_user.user_id)
    # TradeResponse requires new_cash_balance, which doesn't apply to a list
    # of historical entries - populate it with the current balance for each
    # so the schema is satisfied without a separate "history item" schema.
    current_balance = float(get_wallet(db, current_user.user_id))
    for t in trades:
        t.new_cash_balance = current_balance
    return trades
