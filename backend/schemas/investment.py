"""
Pydantic schemas for Investment.
"""

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

ASSET_TYPE = Literal["stock", "mutual_fund", "etf", "bond", "gold", "cash"]


class InvestmentCreate(BaseModel):
    asset_type: ASSET_TYPE
    asset_name: str = Field(min_length=1, max_length=150)
    symbol: Optional[str] = Field(default=None, max_length=20)
    quantity: float = Field(gt=0, description="Units held, must be > 0")
    purchase_price: float = Field(gt=0, description="Price per unit at purchase, must be > 0")
    purchase_date: date
    notes: Optional[str] = Field(default=None, max_length=255)


class InvestmentUpdate(BaseModel):
    asset_name: Optional[str] = Field(default=None, max_length=150)
    symbol: Optional[str] = Field(default=None, max_length=20)
    quantity: Optional[float] = Field(default=None, gt=0)
    purchase_price: Optional[float] = Field(default=None, gt=0)
    purchase_date: Optional[date] = None
    notes: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


class InvestmentResponse(BaseModel):
    investment_id: int
    asset_type: str
    asset_name: str
    symbol: Optional[str] = None
    quantity: float
    purchase_price: float
    purchase_date: date
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime

    # Computed at the schema/service boundary once Part 2 (market data) exists;
    # left optional here so Part 1 can ship without live prices.
    invested_value: Optional[float] = None

    # Populated only when the router asks for market-data enrichment (Part 2).
    # None means "not fetched for this response", not "zero return".
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    return_amount: Optional[float] = None
    return_pct: Optional[float] = None
    price_as_of: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
