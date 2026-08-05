"""
Financial Dashboard
Pydantic schemas for the combined dashboard summary endpoint.
All of these are computed live from Parts 1-3 data - nothing stored here.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SummaryCards(BaseModel):
    total_income: float
    total_expenses: float
    total_savings: float          # THIS MONTH's net savings: total_income - total_expenses. Not the overall pool - see DashboardResponse.savings_pool for that.
    budget_utilization_percent: float   # overall budget spent / overall budget amount, 0 if no overall budget set


class ExpenseBreakdownItem(BaseModel):
    category_id: Optional[int] = None
    category_name: str
    amount: float
    percent_of_total: float


class TrendPoint(BaseModel):
    date: date
    income: float
    expenses: float


class RecentTransactionItem(BaseModel):
    transaction_id: int
    transaction_type: str
    amount: float
    description: Optional[str] = None
    category_name: Optional[str] = None
    payment_mode: Optional[str] = None
    transaction_date: date

    model_config = ConfigDict(from_attributes=True)


class PaymentModeBreakdownItem(BaseModel):
    payment_mode: str
    amount: float
    percent_of_total: float


class DayOfWeekBreakdownItem(BaseModel):
    day_name: str
    amount: float


class DashboardResponse(BaseModel):
    month: date
    summary: SummaryCards
    expense_breakdown: list[ExpenseBreakdownItem]
    payment_mode_breakdown: list[PaymentModeBreakdownItem]
    day_of_week_breakdown: list[DayOfWeekBreakdownItem]
    monthly_trend: list[TrendPoint]
    recent_transactions: list[RecentTransactionItem]
    savings_pool: float = Field(
        default=0.0,
        description="The user's persistent, cumulative savings pool - separate from summary.total_savings, which is just this month's income minus expenses.",
    )
