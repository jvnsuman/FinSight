"""
Investment ORM model - represents a single holding (stock, mutual fund,
ETF, bond, gold, or cash) that a user is tracking as part of their portfolio.

Note: each row is currently a single "lot" (one quantity, one purchase price,
one purchase date). If we later support multiple buys of the same asset,
this model may need to evolve into per-lot rows aggregated by symbol, or
gain a separate InvestmentLot child table.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DATE, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class Investment(Base):
    __tablename__ = "investments"

    investment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    asset_type = Column(String(20), nullable=False)   # "stock" / "mutual_fund" / "etf" / "bond" / "gold" / "cash"
    asset_name = Column(String(150), nullable=False)  # e.g. "HDFC Bank", "SBI Balanced Advantage Fund"
    symbol = Column(String(20), nullable=True, index=True)  # ticker/scheme code used for Alpha Vantage lookups

    quantity = Column(DECIMAL(18, 4), nullable=False)
    purchase_price = Column(DECIMAL(12, 2), nullable=False)   # price per unit at purchase
    purchase_date = Column(DATE, nullable=False)

    notes = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)  # soft-delete: False once a holding is fully sold/removed

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="investments")
