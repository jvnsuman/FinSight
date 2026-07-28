"""
Alert & Notification System
Notification ORM model - an in-app alert generated for a user, either by an
event hook (e.g. a transaction pushes a budget over its limit) or a scheduled
job (e.g. a daily investment-change sweep, a monthly summary).

`type` is kept as a free string (not a DB enum) so new notification types can
be added by any of the three M3 slices without a migration. Suggested values
used across the app: "budget", "investment", "goal", "system" - but services
are free to introduce new ones as needed.
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    title = Column(String(150), nullable=False)
    message = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False, default="system")  # e.g. "budget" / "investment" / "goal" / "system"

    is_read = Column(Boolean, nullable=False, default=False, index=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="notifications")
