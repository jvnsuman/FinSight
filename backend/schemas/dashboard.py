"""
Financial Dashboard
Pydantic schemas for the combined dashboard summary endpoint.
All of these are computed live from Parts 1-3 data - nothing stored here.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SummaryCards(BaseModel):
    total_income: float
    total_expenses: float
    total_savings: float          # total_income - total_expenses
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


class DashboardResponse(BaseModel):
    month: date
    summary: SummaryCards
    expense_breakdown: list[ExpenseBreakdownItem]
    monthly_trend: list[TrendPoint]
    recent_transactions: list[RecentTransactionItem]
