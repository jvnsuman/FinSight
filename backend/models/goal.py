"""
Financial Goal Planning
Goal ORM model - a savings target the user is tracking toward (e.g. "Buy a
Home: ₹50,00,000 by Dec 2030"). Progress is tracked via current_amount, which
the user updates manually for now (a future milestone could tie this to a
linked account/portfolio balance automatically).
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DATE, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class Goal(Base):
    __tablename__ = "goals"

    goal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    goal_name = Column(String(150), nullable=False)   # e.g. "Buy a Home", "Europe Trip"
    goal_type = Column(String(50), nullable=True)      # e.g. "home", "retirement", "travel", "education" - free text for now

    target_amount = Column(DECIMAL(14, 2), nullable=False)
    current_amount = Column(DECIMAL(14, 2), nullable=False, default=0)
    target_date = Column(DATE, nullable=False)

    status = Column(String(20), nullable=False, default="on_track")  # "on_track" / "at_risk" / "completed"

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="goals")
