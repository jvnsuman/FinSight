"""
Budget Monitoring
Pydantic schemas for Budget. Response includes computed utilization fields -
these aren't stored in the DB, they're calculated fresh from transactions each time.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

from backend.schemas.transaction import TransactionResponse


class BudgetCreate(BaseModel):
    category_id: Optional[int] = Field(
        default=None, description="Leave null for an overall total budget covering all spending"
    )
    amount: float = Field(gt=0, description="Budget limit, must be greater than 0")
    month: date = Field(description="Any date within the target month, e.g. 2026-07-01")
    confirm_override: bool = Field(
        default=False,
        description=(
            "Set to true to proceed when the amount exceeds income + available savings "
            "(Tier 3). Leave false on the first attempt; if the API responds with a "
            "confirmation-required error, show the warning to the user and resubmit "
            "with this set to true if they confirm."
        ),
    )

    @field_validator("month")
    @classmethod
    def normalize_to_first_of_month(cls, v: date) -> date:
        return v.replace(day=1)


class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(default=None, gt=0)
    confirm_override: bool = Field(default=False, description="Same as in BudgetCreate, for amount changes.")


class BudgetResponse(BaseModel):
    budget_id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = Field(default=None, description="Null means this is an overall total budget")
    amount: float
    month: date

    # --- Computed fields (not stored - calculated live from transactions) ---
    spent_amount: float
    remaining_amount: float
    utilization_percent: float
    is_exceeded: bool
    income_warning: Optional[str] = Field(
        default=None,
        description="Set when this budget's amount draws on savings (Tier 2) or exceeded income+savings and was confirmed (Tier 3). Null for Tier 1.",
    )

    model_config = ConfigDict(from_attributes=True)


class BudgetDetailResponse(BudgetResponse):
    """
    Same fields as BudgetResponse, plus the actual list of expense
    transactions that make up spent_amount this month - used by the "click a
    budget to see its breakdown" popup on the frontend. Ordered most recent
    first, same as the main transactions list.
    """
    transactions: list[TransactionResponse] = Field(default_factory=list)
