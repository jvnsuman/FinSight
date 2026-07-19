"""
Investment service - CRUD logic for a user's portfolio holdings.
"""

from sqlalchemy.orm import Session

from backend.models.investment import Investment
from backend.schemas.investment import InvestmentCreate, InvestmentUpdate


def _with_invested_value(investment: Investment) -> Investment:
    """
    Attaches invested_value (quantity * purchase_price) as a transient attribute
    so it flows through InvestmentResponse without needing a DB column.
    Cheap to compute here; current/market value comes later in Part 2.
    """
    investment.invested_value = float(investment.quantity) * float(investment.purchase_price)
    return investment


def create_investment(db: Session, user_id: int, data: InvestmentCreate) -> Investment:
    investment = Investment(
        user_id=user_id,
        asset_type=data.asset_type,
        asset_name=data.asset_name,
        symbol=data.symbol,
        quantity=data.quantity,
        purchase_price=data.purchase_price,
        purchase_date=data.purchase_date,
        notes=data.notes,
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return _with_invested_value(investment)


def get_user_investments(db: Session, user_id: int, include_inactive: bool = False) -> list[Investment]:
    query = db.query(Investment).filter(Investment.user_id == user_id)
    if not include_inactive:
        query = query.filter(Investment.is_active.is_(True))
    investments = query.order_by(Investment.purchase_date.desc()).all()
    return [_with_invested_value(inv) for inv in investments]


def get_investment_or_404(db: Session, user_id: int, investment_id: int) -> Investment:
    investment = (
        db.query(Investment)
        .filter(Investment.investment_id == investment_id, Investment.user_id == user_id)
        .first()
    )
    if not investment:
        raise ValueError("Investment not found")
    return _with_invested_value(investment)


def update_investment(db: Session, user_id: int, investment_id: int, updates: InvestmentUpdate) -> Investment:
    investment = get_investment_or_404(db, user_id, investment_id)
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(investment, field, value)
    db.commit()
    db.refresh(investment)
    return _with_invested_value(investment)


def delete_investment(db: Session, user_id: int, investment_id: int) -> None:
    """
    Soft-delete: marks the holding inactive rather than removing it, so
    historical returns and portfolio-over-time charts (Part 4) stay intact
    even after a position is fully sold.
    """
    investment = get_investment_or_404(db, user_id, investment_id)
    investment.is_active = False
    db.commit()


def with_market_data(db: Session, investments: list[Investment]) -> list[Investment]:
    """
    Enriches a list of investments with live/cached price + return data
    (Part 2). Kept separate from get_user_investments so plain CRUD callers
    don't pay for market data lookups they don't need.
    """
    # Local imports to avoid a hard dependency from investment_service -> market
    # data / analytics on every import of this module, since most CRUD callers
    # (add/edit/delete) never need them.
    from backend.services import market_data_service, analytics_service

    symbols = [inv.symbol for inv in investments if inv.symbol]
    prices = market_data_service.get_prices(db, symbols)

    for inv in investments:
        price = prices.get(inv.symbol) if inv.symbol else None
        returns = analytics_service.compute_return(inv, price)
        inv.invested_value = returns["invested_value"]
        inv.current_value = returns["current_value"]
        inv.return_amount = returns["return_amount"]
        inv.return_pct = returns["return_pct"]
        inv.current_price = returns["current_price"]
        inv.price_as_of = returns["price_as_of"]

    return investments
