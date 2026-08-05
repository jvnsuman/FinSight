"""
Pydantic schemas for the savings pool breakdown - the "click to see details"
popup for the Savings Pool card on the dashboard.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SavingsGoalAllocation(BaseModel):
    """How much of the user's active goal funding currently sits in each goal."""
    goal_id: int
    goal_name: str
    current_amount: float


class SavingsBreakdownResponse(BaseModel):
    savings_pool: float = Field(description="Current total in the persistent savings pool - the overall/cumulative savings figure.")
    this_month_contribution: float = Field(
        description="This calendar month's income minus expenses, already swept into savings_pool once per month (0 if the month went negative)."
    )
    wallet_cash_pending_sweep: float = Field(
        description="Cash currently sitting in the trading wallet (cash_balance) that hasn't been swept into the pool yet - happens automatically at next month's refill."
    )
    total_allocated_to_goals: float = Field(
        description="Sum of current_amount across all of the user's goals - money that has already left the pool and is earmarked toward a specific goal."
    )
    goal_allocations: list[SavingsGoalAllocation] = Field(default_factory=list)
    last_refill_month: Optional[str] = Field(
        default=None,
        description="The month (YYYY-MM-01) whose income-minus-expenses last_refill_amount was actually credited from - e.g. July for a refill that triggered in August. Null if the pool has never been refilled.",
    )
    last_refill_triggered_month: Optional[str] = Field(
        default=None,
        description="The month (YYYY-MM-01) the most recent top-up actually happened in - always one month after last_refill_month, since a refill triggered in August credits July's savings.",
    )
    last_refill_amount: float = Field(
        default=0.0,
        description="The exact amount added to the pool at the most recent monthly refill - the previous month's income-minus-expenses (floored at 0) plus whatever wallet cash was swept in at that same moment.",
    )
