"""
Pydantic schemas for Account.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

ACCOUNT_TYPE = Literal["bank", "card", "wallet"]

class AccountCreate(BaseModel):
    account_name: str = Field(min_length=2, max_length=100)
    account_type: ACCOUNT_TYPE
    bank_name: Optional [str] = Field(default=None, max_length=100)
    account_number: Optional[str] = Field(default=None, max_length=50)
    balance: float= Field(default=0, ge=0, description="Starting balance, must be >= 0")


class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    bank_name: Optional[str]=None
    account_number: Optional[str] = None
    is_active: Optional[bool] = None


class AccountResponse(BaseModel):
    account_id: int
    account_name: str
    account_type: str
    bank_name: Optional[str] = None
    account_number: Optional[str] =None
    balance: float
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)