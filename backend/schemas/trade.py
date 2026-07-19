"""
Pydantic schemas for the simulated trading wallet and buy/sell actions.
"""

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

ASSET_TYPE = Literal["stock", "mutual_fund", "etf", "bond", "gold", "cash"]


class WalletResponse(BaseModel):
    cash_balance: float
    savings_pool: float


class DepositRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount to add to the simulated cash wallet")


class BuyRequest(BaseModel):
    asset_type: ASSET_TYPE
    asset_name: str = Field(min_length=1, max_length=150)
    symbol: Optional[str] = Field(default=None, max_length=20)
    quantity: float = Field(gt=0)
    # price is optional: if omitted, the current cached/live market price is used
    # (falls back to rejecting the trade if no price is available at all - see
    # trade_service.execute_buy for the exact rule).
    price: Optional[float] = Field(default=None, gt=0)


class SellRequest(BaseModel):
    investment_id: int
    quantity: float = Field(gt=0)
    price: Optional[float] = Field(default=None, gt=0)


class TradeResponse(BaseModel):
    trade_id: int
    action: str
    asset_type: Optional[str] = None
    asset_name: Optional[str] = None
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    cash_amount: float
    trade_date: date
    created_at: datetime

    # Returned alongside the trade so the frontend can update the wallet
    # display without a second round-trip.
    new_cash_balance: float

    class Config:
        from_attributes = True
