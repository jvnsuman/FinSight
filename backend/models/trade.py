"""
Simulated Trading - Trade ORM model.

An append-only log of every buy, sell, or wallet deposit a user makes.
Unlike Investment (which reflects current holdings), this table is never
updated or soft-deleted - it's the audit trail of how the current state
was reached, and is what a future "trade history" screen would read from.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DATE, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class Trade(Base):
    __tablename__ = "trades"

    trade_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    investment_id = Column(Integer, ForeignKey("investments.investment_id"), nullable=True, index=True)

    action = Column(String(10), nullable=False)  # "buy" / "sell" / "deposit"
    asset_type = Column(String(20), nullable=True)   # denormalized copy, so history survives even if the holding is later deleted
    asset_name = Column(String(150), nullable=True)
    symbol = Column(String(20), nullable=True)

    quantity = Column(DECIMAL(18, 4), nullable=True)  # null for a plain cash deposit
    price = Column(DECIMAL(12, 2), nullable=True)      # price per unit at time of trade; null for deposit
    cash_amount = Column(DECIMAL(14, 2), nullable=False)  # +ve = cash added to wallet, -ve = cash removed

    trade_date = Column(DATE, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="trades")
