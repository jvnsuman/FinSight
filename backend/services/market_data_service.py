"""
Market data service - fetches current prices via Yahoo Finance (yfinance),
with a DB-backed cache to avoid spamming the API unnecessarily.

Design:
  - Every price lookup goes through get_price(), which checks PriceCache first.
  - A cache hit within MARKET_DATA_CACHE_TTL_MINUTES is returned without any
    network call.
  - A cache miss/stale entry triggers a live call via yfinance.
  - If the live call fails, we fall back to the last cached price (even if stale) 
    rather than raising - a slightly old price is far more useful to the user 
    than a blank portfolio.
"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional

import yfinance as yf
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.price_cache import PriceCache
from backend.models.investment import Investment


class MarketDataError(Exception):
    """Raised only when we have neither a live price nor any cached price at all."""


def _fetch_live_quote(symbol: str) -> Optional[dict]:
    """
    Calls Yahoo Finance for a single symbol.
    Returns a dict with price/previous_close/latest_trading_day, or None if
    the symbol wasn't found or an error occurred.
    """
    def _try_fetch(sym: str) -> Optional[dict]:
        try:
            ticker = yf.Ticker(sym)
            # fast_info is much faster than history() or info and doesn't scrape as much
            fast_info = ticker.fast_info
            
            price = fast_info.last_price
            prev_close = fast_info.previous_close
            
            if price is None:
                return None
                
            return {
                "price": Decimal(str(price)),
                "previous_close": Decimal(str(prev_close)) if prev_close else None,
                "latest_trading_day": str(date.today()), # fast_info doesn't easily expose the exact timestamp of last trade without heavier calls
            }
        except Exception:
            # Network failure, bad symbol, etc - fallback to cache
            return None

    result = _try_fetch(symbol)
    if result is not None:
        return result
        
    # If the exact symbol failed and has no suffix, try common Indian market suffixes
    if "." not in symbol:
        for suffix in [".NS", ".BO"]:
            result = _try_fetch(symbol + suffix)
            if result is not None:
                return result
                
    return None


def get_price(db: Session, symbol: str, force_refresh: bool = False) -> Optional[PriceCache]:
    """
    Returns the best available PriceCache row for a symbol, or None if we've
    never successfully fetched this symbol and can't reach yfinance now.
    """
    if not symbol:
        return None

    cached = db.query(PriceCache).filter(PriceCache.symbol == symbol).first()

    cache_is_fresh = (
        cached is not None
        and datetime.utcnow() - cached.fetched_at < timedelta(minutes=settings.MARKET_DATA_CACHE_TTL_MINUTES)
    )
    if cache_is_fresh and not force_refresh:
        return cached

    live = _fetch_live_quote(symbol)

    if live is None:
        # Live fetch failed or symbol not recognized - fall back to cache.
        return cached

    if cached is None:
        cached = PriceCache(symbol=symbol)
        db.add(cached)

    cached.price = live["price"]
    cached.previous_close = live["previous_close"]
    cached.latest_trading_day = live["latest_trading_day"]
    cached.fetched_at = datetime.utcnow()
    db.commit()
    db.refresh(cached)
    return cached


def get_prices(db: Session, symbols: list[str]) -> dict[str, PriceCache]:
    """
    Batched version of get_price for multiple symbols (e.g. rendering a full portfolio).
    """
    result: dict[str, PriceCache] = {}
    unique_symbols = {s for s in symbols if s}
    for symbol in unique_symbols:
        price = get_price(db, symbol)
        if price is not None:
            result[symbol] = price
    return result


def refresh_all_active_symbols(db: Session):
    """
    Background job function to refresh prices for all distinct active symbols.
    """
    active_symbols = (
        db.query(Investment.symbol)
        .filter(Investment.is_active.is_(True), Investment.symbol.isnot(None))
        .distinct()
        .all()
    )
    
    symbols = [row[0] for row in active_symbols if row[0]]
    for symbol in symbols:
        get_price(db, symbol, force_refresh=True)
