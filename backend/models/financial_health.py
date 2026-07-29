from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class FinancialHealthCache(Base):
    __tablename__ = "financial_health_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False, index=True)
    
    score = Column(Integer, nullable=False)
    metrics_json = Column(JSON, nullable=False)
    ai_insights_json = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
