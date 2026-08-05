"""
API routers for managing investment holdings (stocks, mutual funds, ETFs, bonds, etc.)
and the market-data-enriched views built on top of them.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.investment import InvestmentCreate, InvestmentUpdate, InvestmentResponse
from backend.schemas.portfolio import PortfolioSummaryResponse
from backend.services.investment_service import (
    create_investment,
    get_user_investments,
    get_investment_or_404,
    update_investment,
    delete_investment,
    with_market_data,
)
from backend.services import market_data_service, analytics_service

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
def add_investment(
    data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new investment holding to the user's portfolio."""
    return create_investment(db, current_user.user_id, data)


@router.get("", response_model=list[InvestmentResponse])
def list_investments(
    include_inactive: bool = False,
    include_market_data: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all holdings for the current user.

    include_market_data=true additionally populates current_price,
    current_value, return_amount, and return_pct for each holding, fetched
    via Alpha Vantage (cached; see market_data_service).
    """
    investments = get_user_investments(db, current_user.user_id, include_inactive)
    if include_market_data:
        investments = with_market_data(db, investments)
    return investments


# NOTE: this must be declared before "/{investment_id}" - otherwise FastAPI
# would try to parse "summary" as an investment_id and 422 on every call.
@router.get("/summary/allocation", response_model=PortfolioSummaryResponse)
def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Portfolio-level totals and asset-type allocation, using live/cached
    market prices. Feeds the allocation donut and returns strip (Part 4).
    """
    investments = get_user_investments(db, current_user.user_id, include_inactive=False)
    symbols = [inv.symbol for inv in investments if inv.symbol]
    prices = market_data_service.get_prices(db, symbols)
    return analytics_service.compute_portfolio_summary(investments, prices)


@router.get("/{investment_id}", response_model=InvestmentResponse)
def get_investment(
    investment_id: int,
    include_market_data: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        investment = get_investment_or_404(db, current_user.user_id, investment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if include_market_data:
        [investment] = with_market_data(db, [investment])
    return investment


@router.put("/{investment_id}", response_model=InvestmentResponse)
def edit_investment(
    investment_id: int,
    updates: InvestmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_investment(db, current_user.user_id, investment_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_investment(
    investment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-deletes the holding (marks inactive) - historical return data is preserved."""
    try:
        delete_investment(db, current_user.user_id, investment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
