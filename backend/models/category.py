"""
Category ORM model - used to clarify transactions(Food, Transport, Salary, etc.)
Supports both system-seeded default and user-created custom categories.
"""

from  sqlalchemy import Column, Integer, String,  Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship

from backend.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    category_name = Column(String(100), nullable=False)
    category_type = Column(String(20), nullable=False)      #"income" / "expense"
    icon = Column(String(50), nullable=True)                # optional icon identifier for frontend
    is_default = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")
    