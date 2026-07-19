"""
Account ORM model - represents a bank account, card, or wallet the  user track money in.
"""

from sqlalchemy  import Column, Integer, String, DECIMAL, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    account_name = Column(String(100), nullable=False)    #e.g. "HDFC savings"
    account_type = Column(String(20), nullable=False)     #"bank" / "card" / "wallet"
    bank_name = Column(String(100), nullable=True)        #e.g. "HDFC", "ICICI"
    account_number = Column(String(50), nullable=True)    #last 4 digits or masked reference
    balance = Column(DECIMAL(12, 2), default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    