"""
PriceCache ORM model - stores the most recently fetched market price per symbol.

Alpha Vantage's free tier allows only 25 requests/day (5/minute), so we cannot
fetch a fresh price on every request that touches a holding. Instead, every
price lookup goes through this cache first; we only call the API when a
symbol's cached price is missing or older than MARKET_DATA_CACHE_TTL_MINUTES.

One row per symbol (shared across users - two users holding the same stock
share one cached price, which also helps stretch the daily quota further).
"""

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, func

from backend.database import Base


class PriceCache(Base):
    __tablename__ = "price_cache"

    symbol = Column(String(20), primary_key=True)
    price = Column(DECIMAL(14, 4), nullable=False)
    previous_close = Column(DECIMAL(14, 4), nullable=True)
    latest_trading_day = Column(String(20), nullable=True)  # as returned by Alpha Vantage, e.g. "2026-07-15"

    fetched_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
