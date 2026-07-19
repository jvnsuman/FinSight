"""
Budget Monitoring
Budget ORM model - a spending limit for given month, either scoped to one 
category (e.g. "food & dining: ₹8,000")
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, index=True)
    user_id  = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    
    # NULL category_id = an overall total budget covering all spending that month
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True, index=True)

    amount = Column(DECIMAL(12, 2), nullable=False)          # the limit
    month = Column(Date, nullable=False)                      # stored as the 1st of the month, e.g. 2026-07-01

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
    