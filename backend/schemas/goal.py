"""
Pydantic schemas for Goal.
"""

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class GoalCreate(BaseModel):
    goal_name: str = Field(min_length=1, max_length=150)
    goal_type: Optional[str] = Field(default=None, max_length=50)
    target_amount: float = Field(gt=0, description="Target amount, must be > 0")
    current_amount: float = Field(default=0, ge=0, description="Amount already saved toward this goal")
    target_date: date

    @field_validator("target_date")
    @classmethod
    def target_date_must_be_future(cls, v: date) -> date:
        if v <= date.today():
            raise ValueError("target_date must be in the future")
        return v


class GoalUpdate(BaseModel):
    goal_name: Optional[str] = Field(default=None, max_length=150)
    goal_type: Optional[str] = Field(default=None, max_length=50)
    target_amount: Optional[float] = Field(default=None, gt=0)
    current_amount: Optional[float] = Field(default=None, ge=0)
    target_date: Optional[date] = None

    @field_validator("target_date")
    @classmethod
    def target_date_must_be_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v <= date.today():
            raise ValueError("target_date must be in the future")
        return v


class GoalResponse(BaseModel):
    goal_id: int
    goal_name: str
    goal_type: Optional[str] = None
    target_amount: float
    current_amount: float
    target_date: date
    status: str
    created_at: datetime

    # Computed at the service boundary, not stored directly
    progress_pct: float
    amount_remaining: float
    days_remaining: int
    required_monthly_saving: Optional[float] = None  # None if target_date has already passed

    model_config = ConfigDict(from_attributes=True)


class AllocateSavingsRequest(BaseModel):
    source: Literal["wallet", "income_savings"] = Field(
        description="'wallet' = simulated trading cash balance; "
                    "'income_savings' = the persistent savings pool, refilled "
                    "monthly from income minus expenses plus wallet sweep"
    )
    percent: float = Field(gt=0, le=100, description="Percent of the source amount to allocate across goals")


class GoalAllocationLine(BaseModel):
    goal_id: int
    goal_name: str
    amount_allocated: float
    new_current_amount: float
    new_progress_pct: float


class AllocateSavingsResponse(BaseModel):
    source: str
    source_amount: float
    percent_applied: float
    total_allocated: float
    allocations: list[GoalAllocationLine]


class GoalWithdrawal(BaseModel):
    goal_id: int
    amount: float = Field(gt=0)


class CoverShortfallRequest(BaseModel):
    withdrawals: list[GoalWithdrawal] = Field(
        min_length=1,
        description="Which goal(s) to pull the shortfall from, and how much from each. "
                    "The amounts should sum to the shortfall you're covering, but this "
                    "isn't enforced - you can cover a partial amount if you prefer."
    )


class CoverShortfallResponse(BaseModel):
    total_withdrawn: float
    updated_goals: list[GoalAllocationLine]


class FundGoalRequest(BaseModel):
    source: Literal["wallet", "income_savings"] = Field(
        description="'wallet' = simulated trading cash balance; "
                    "'income_savings' = the persistent savings pool"
    )
    amount: Optional[float] = Field(default=None, gt=0, description="Fixed amount to fund this goal with")
    percent: Optional[float] = Field(default=None, gt=0, le=100, description="Percent of the source amount to fund this goal with")

    @model_validator(mode="after")
    def exactly_one_of_amount_or_percent(self):
        if (self.amount is None) == (self.percent is None):
            raise ValueError("Provide exactly one of 'amount' or 'percent', not both and not neither.")
        return self


class FundGoalResponse(BaseModel):
    goal_id: int
    goal_name: str
    source: str
    amount_funded: float
    new_current_amount: float
    new_progress_pct: float
    remaining_source_balance: float
