"""
Trade service - simulated buy/sell/deposit logic.

Important: this is entirely simulated. No real money moves. cash_balance is
an in-app number the user funds manually and trades against.

Buy behavior: if the user already holds this symbol (matched by symbol if
provided, otherwise by asset_name), the buy is AVERAGED into the existing
Investment row rather than creating a new lot. This was a deliberate choice
to avoid a bigger multi-lot schema change - it means purchase_price becomes
a weighted average cost basis, not the price of any single purchase. If
per-lot history is ever needed, the Trade table already has the full
transaction-level detail to reconstruct it later.

Sell behavior: reduces quantity on the matched holding. Selling the full
quantity soft-deletes the holding (is_active = False), consistent with how
manual deletes already work.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.investment import Investment
from backend.models.trade import Trade
from backend.models.user import User
from backend.schemas.trade import BuyRequest, SellRequest


class TradeError(Exception):
    """Raised for user-facing trade failures (insufficient funds, no price available, etc.)."""


def _resolve_price(db: Session, symbol: Optional[str], explicit_price: Optional[float]) -> Decimal:
    """
    Determines the price to execute a trade at: an explicitly supplied price
    takes priority (lets the frontend show a price then submit exactly that
    price); otherwise falls back to the cached/live market price for the
    symbol via market_data_service.
    """
    if explicit_price is not None:
        return Decimal(str(explicit_price))

    if not symbol:
        raise TradeError("A price must be provided when no symbol is set (cannot look up a market price).")

    # Local import to avoid a hard dependency for callers that always pass an
    # explicit price and never need market_data_service loaded.
    from backend.services import market_data_service

    cached = market_data_service.get_price(db, symbol)
    if cached is None:
        raise TradeError(f"No market price available for '{symbol}'. Please supply a price manually.")
    return Decimal(cached.price)


def get_wallet(db: Session, user_id: int) -> Decimal:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise TradeError("User not found")
    return user.cash_balance


def deposit(db: Session, user_id: int, amount: float) -> Trade:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise TradeError("User not found")

    deposit_amount = Decimal(str(amount))
    
    if deposit_amount > user.savings_pool:
        raise TradeError(f"Insufficient funds in Savings Pool. You only have {float(user.savings_pool):.2f} available to transfer.")

    user.savings_pool -= deposit_amount
    user.cash_balance = Decimal(user.cash_balance) + deposit_amount

    trade = Trade(
        user_id=user_id,
        action="deposit",
        cash_amount=deposit_amount,
        trade_date=date.today(),
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    trade.new_cash_balance = float(user.cash_balance)
    return trade


def execute_buy(db: Session, user_id: int, data: BuyRequest) -> Trade:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise TradeError("User not found")

    price = _resolve_price(db, data.symbol, data.price)
    quantity = Decimal(str(data.quantity))
    cost = quantity * price

    if cost > Decimal(user.cash_balance):
        raise TradeError(
            f"Insufficient funds: this trade costs {float(cost):.2f} but your wallet balance is {float(user.cash_balance):.2f}."
        )

    # Match an existing active holding by symbol (preferred) or asset_name,
    # so repeat buys of the same asset average in rather than creating
    # duplicate rows.
    existing = None
    query = db.query(Investment).filter(Investment.user_id == user_id, Investment.is_active.is_(True))
    if data.symbol:
        existing = query.filter(Investment.symbol == data.symbol).first()
    else:
        existing = query.filter(Investment.asset_name == data.asset_name, Investment.symbol.is_(None)).first()

    if existing:
        existing_quantity = Decimal(existing.quantity)
        existing_cost_basis = existing_quantity * Decimal(existing.purchase_price)
        new_quantity = existing_quantity + quantity
        new_avg_price = (existing_cost_basis + cost) / new_quantity
        existing.quantity = new_quantity
        existing.purchase_price = new_avg_price
        investment = existing
    else:
        investment = Investment(
            user_id=user_id,
            asset_type=data.asset_type,
            asset_name=data.asset_name,
            symbol=data.symbol,
            quantity=quantity,
            purchase_price=price,
            purchase_date=date.today(),
        )
        db.add(investment)

    user.cash_balance = Decimal(user.cash_balance) - cost
    db.flush()  # ensure investment.investment_id is populated before the Trade references it

    trade = Trade(
        user_id=user_id,
        investment_id=investment.investment_id,
        action="buy",
        asset_type=data.asset_type,
        asset_name=data.asset_name,
        symbol=data.symbol,
        quantity=quantity,
        price=price,
        cash_amount=-cost,
        trade_date=date.today(),
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    trade.new_cash_balance = float(user.cash_balance)
    return trade


def execute_sell(db: Session, user_id: int, data: SellRequest) -> Trade:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise TradeError("User not found")

    investment = (
        db.query(Investment)
        .filter(
            Investment.investment_id == data.investment_id,
            Investment.user_id == user_id,
            Investment.is_active.is_(True),
        )
        .first()
    )
    if not investment:
        raise TradeError("Holding not found")

    sell_quantity = Decimal(str(data.quantity))
    held_quantity = Decimal(investment.quantity)
    if sell_quantity > held_quantity:
        raise TradeError(f"Cannot sell {sell_quantity} units - you only hold {held_quantity}.")

    price = _resolve_price(db, investment.symbol, data.price)
    proceeds = sell_quantity * price

    remaining = held_quantity - sell_quantity
    if remaining == 0:
        investment.is_active = False
        investment.quantity = Decimal("0")
    else:
        investment.quantity = remaining
        # purchase_price (avg cost basis) is intentionally left unchanged on a
        # partial sell - the remaining units still carry the original average
        # cost, which is what makes the return % on the remainder meaningful.

    user.cash_balance = Decimal(user.cash_balance) + proceeds

    trade = Trade(
        user_id=user_id,
        investment_id=investment.investment_id,
        action="sell",
        asset_type=investment.asset_type,
        asset_name=investment.asset_name,
        symbol=investment.symbol,
        quantity=sell_quantity,
        price=price,
        cash_amount=proceeds,
        trade_date=date.today(),
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    trade.new_cash_balance = float(user.cash_balance)
    return trade


def get_trade_history(db: Session, user_id: int) -> list[Trade]:
    return (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .order_by(Trade.created_at.desc())
        .all()
    )
