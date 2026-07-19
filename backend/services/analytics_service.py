"""
Analytics service - return and asset allocation calculations for a portfolio.

Return method: SIMPLE RETURN, not XIRR.
  return_amount = current_value - invested_value
  return_pct    = return_amount / invested_value * 100

This is the right fit for the current data model: each Investment row is a
single lot (one quantity, one purchase price, one purchase date). With a
single cash flow in and one valuation out, XIRR mathematically reduces to
this same figure anyway - it only earns its complexity once a holding can
have multiple buys at different dates. If/when that lands, this is the only
module that should need to change.
"""

from decimal import Decimal
from typing import Optional

from backend.models.investment import Investment
from backend.models.price_cache import PriceCache


def compute_current_value(investment: Investment, price: Optional[PriceCache]) -> Decimal:
    """
    Current market value of a holding. Falls back to invested value (i.e. a
    flat/zero return) if we have no price data at all for this symbol yet -
    better than showing a blank or crashing the dashboard.
    """
    invested_value = Decimal(investment.quantity) * Decimal(investment.purchase_price)
    if price is None:
        return invested_value
    return Decimal(investment.quantity) * price.price


def compute_return(investment: Investment, price: Optional[PriceCache]) -> dict:
    """
    Returns a dict with invested_value, current_value, return_amount, return_pct
    for a single holding.
    """
    invested_value = Decimal(investment.quantity) * Decimal(investment.purchase_price)
    current_value = compute_current_value(investment, price)
    return_amount = current_value - invested_value
    return_pct = (return_amount / invested_value * 100) if invested_value > 0 else Decimal(0)

    return {
        "invested_value": float(invested_value),
        "current_value": float(current_value),
        "return_amount": float(return_amount),
        "return_pct": float(return_pct),
        "current_price": float(price.price) if price else None,
        "price_as_of": price.latest_trading_day if price else None,
    }


def compute_portfolio_summary(investments: list[Investment], prices: dict[str, PriceCache]) -> dict:
    """
    Aggregates total invested/current value, overall return, and allocation
    percentages by asset_type across a list of holdings.
    """
    total_invested = Decimal(0)
    total_current = Decimal(0)
    allocation_by_type: dict[str, Decimal] = {}

    for inv in investments:
        price = prices.get(inv.symbol) if inv.symbol else None
        invested_value = Decimal(inv.quantity) * Decimal(inv.purchase_price)
        current_value = compute_current_value(inv, price)

        total_invested += invested_value
        total_current += current_value
        allocation_by_type[inv.asset_type] = allocation_by_type.get(inv.asset_type, Decimal(0)) + current_value

    total_return_amount = total_current - total_invested
    total_return_pct = (total_return_amount / total_invested * 100) if total_invested > 0 else Decimal(0)

    allocation = []
    for asset_type, value in allocation_by_type.items():
        pct = (value / total_current * 100) if total_current > 0 else Decimal(0)
        allocation.append({
            "asset_type": asset_type,
            "value": float(value),
            "percentage": float(pct),
        })
    # Largest allocation first - matches how the spec doc's donut/legend is ordered.
    allocation.sort(key=lambda a: a["value"], reverse=True)

    return {
        "total_invested": float(total_invested),
        "total_current_value": float(total_current),
        "total_return_amount": float(total_return_amount),
        "total_return_pct": float(total_return_pct),
        "allocation": allocation,
    }
