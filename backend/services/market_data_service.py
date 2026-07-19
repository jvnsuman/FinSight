"""
Market data service - fetches current prices via the Alpha Vantage GLOBAL_QUOTE
endpoint, with a DB-backed cache to respect the free-tier limit of 25
requests/day (5/minute).

Design:
  - Every price lookup goes through get_price(), which checks PriceCache first.
  - A cache hit within MARKET_DATA_CACHE_TTL_MINUTES is returned without any
    network call.
  - A cache miss/stale entry triggers a live call ONLY if we're still under
    ALPHA_VANTAGE_DAILY_REQUEST_LIMIT for the current day (tracked in-process;
    see _daily_call_tracker note below).
  - If the live call fails or the quota is exhausted, we fall back to the
    last cached price (even if stale) rather than raising - a slightly old
    price is far more useful to the user than a blank portfolio.
"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.price_cache import PriceCache


class MarketDataError(Exception):
    """Raised only when we have neither a live price nor any cached price at all."""


# NOTE: This tracks Alpha Vantage calls made since process start, in memory.
# It resets on every backend restart, so it under-counts rather than over-counts
# across restarts - safe direction to be wrong in, since the real backstop is
# Alpha Vantage's own 429/"Information" response when the quota is actually hit.
# A more robust version would persist this counter in the DB, keyed by date;
# worth revisiting if the team hits real quota problems in practice.
_daily_call_tracker = {"date": None, "count": 0}


def _calls_remaining_today() -> int:
    today = date.today()
    if _daily_call_tracker["date"] != today:
        _daily_call_tracker["date"] = today
        _daily_call_tracker["count"] = 0
    return settings.ALPHA_VANTAGE_DAILY_REQUEST_LIMIT - _daily_call_tracker["count"]


def _record_call_made() -> None:
    today = date.today()
    if _daily_call_tracker["date"] != today:
        _daily_call_tracker["date"] = today
        _daily_call_tracker["count"] = 0
    _daily_call_tracker["count"] += 1


def _fetch_live_quote(symbol: str) -> Optional[dict]:
    """
    Calls Alpha Vantage's GLOBAL_QUOTE endpoint for a single symbol.
    Returns a dict with price/previous_close/latest_trading_day, or None if
    the symbol wasn't found or Alpha Vantage returned a rate-limit notice.
    """
    if not settings.ALPHA_VANTAGE_API_KEY:
        return None

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
    }
    try:
        response = httpx.get(settings.ALPHA_VANTAGE_BASE_URL, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, httpx.TimeoutException, ValueError):
        # Network failure, timeout, non-2xx status, or unparseable JSON - treat
        # exactly like "symbol not found": caller falls back to cache/invested
        # value. A flaky Alpha Vantage call should never take down the
        # investments or portfolio-summary endpoints.
        return None

    # Alpha Vantage doesn't use HTTP error codes for rate limiting / bad symbols -
    # it returns 200 with an "Information" or "Note" key instead, or an empty
    # "Global Quote" object for an unrecognized symbol.
    if "Information" in data or "Note" in data:
        return None

    quote = data.get("Global Quote") or {}
    price_raw = quote.get("05. price")
    if not price_raw:
        return None

    return {
        "price": Decimal(price_raw),
        "previous_close": Decimal(quote["08. previous close"]) if quote.get("08. previous close") else None,
        "latest_trading_day": quote.get("07. latest trading day"),
    }


def get_price(db: Session, symbol: str, force_refresh: bool = False) -> Optional[PriceCache]:
    """
    Returns the best available PriceCache row for a symbol, or None if we've
    never successfully fetched this symbol and can't reach Alpha Vantage now.

    Does NOT raise on quota exhaustion or network failure - falls back to
    whatever is cached, however stale, since a stale price beats no price.
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

    if _calls_remaining_today() <= 0:
        # Quota exhausted for today - serve whatever we have, even if stale.
        return cached

    live = _fetch_live_quote(symbol)
    _record_call_made()

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
    Batched version of get_price for multiple symbols (e.g. rendering a full
    portfolio). Still respects the shared daily quota - symbols beyond the
    remaining call budget simply fall back to their existing cache entry (or
    are omitted if never cached).
    """
    result: dict[str, PriceCache] = {}
    unique_symbols = {s for s in symbols if s}
    for symbol in unique_symbols:
        price = get_price(db, symbol)
        if price is not None:
            result[symbol] = price
    return result
