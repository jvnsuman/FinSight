"""
Pydantic schemas for portfolio-level analytics (allocation + aggregate returns).
"""

from pydantic import BaseModel


class AllocationSlice(BaseModel):
    asset_type: str
    value: float
    percentage: float


class PortfolioSummaryResponse(BaseModel):
    total_invested: float
    total_current_value: float
    total_return_amount: float
    total_return_pct: float
    allocation: list[AllocationSlice]
