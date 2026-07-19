"""
Transaction ORM model - a single income/expense/transfer record, linked to an
account and a category.
"""
from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.account_id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True, index=True)
    
    transaction_type = Column(String(20), nullable=False)  # "income" / "expense" / "transfer"
    amount = Column(DECIMAL(12, 2), nullable=False)
    description = Column(String(255), nullable=True)
    payment_mode = Column(String(255), nullable=True)
    transaction_date = Column(Date, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship ("User", back_populates="transactions")
    account = relationship ("Account",  back_populates="transactions")
    category = relationship ("Category", back_populates="transactions")