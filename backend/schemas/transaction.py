"""
Pydantic schemas for transaction.
"""

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

from backend.schemas.category import CategoryResponse

TRANSACTION_TYPES = Literal["income", "expense", "transfer"]

class TransactionCreate(BaseModel):
    account_id: int
    category_id: Optional[int] =  None
    transaction_type: TRANSACTION_TYPES
    amount: float = Field(gt=0, description="Must be greater than 0")
    description: Optional[str] = Field(default=None, max_length=255)
    payment_mode: Optional[str] = Field(default=None, max_length=30)
    transaction_date: date


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None
    payment_mode: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionResponse(BaseModel):
    transaction_id: int
    account_id: int
    category: Optional[CategoryResponse] = None
    transaction_type: str
    amount: float
    description: Optional[str]  = None
    payment_mode: Optional[str] = None
    transaction_date: date
    created_at: datetime

    # Populated only for an expense that exceeded the available savings_pool.
    # None means "no shortfall" - not present at all in the vast majority of
    # transactions, so existing frontend code that ignores this field is
    # unaffected.
    savings_warning: Optional["SavingsShortfallWarning"] = None

    model_config = ConfigDict(from_attributes=True)


class SavingsShortfallWarning(BaseModel):
    message: str
    savings_pool_before: float
    amount_covered_by_savings: float
    remaining_shortfall: float
    savings_pool_after: float