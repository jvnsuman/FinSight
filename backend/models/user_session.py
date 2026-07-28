"""
Session Management (login alerts + selective device logout)

UserSession ORM model - one row per successful login, used to:
  1. Let a user see every device/browser currently logged into their account.
  2. Let them revoke ONE session (log out that device) without touching any
     others - something a single `token_version` bump cannot do, since that
     invalidates every token at once.

How this plugs into auth:
  - Every JWT now carries a `sid` claim = this row's `session_id`.
  - `get_current_user` (backend/core/dependencies.py) checks that the
    session referenced by `sid` still has `is_active=True`. Revoking a
    session (is_active -> False) makes that JWT stop working on its very
    next request, even though the JWT itself hasn't expired.
  - `token_version` is untouched by this feature and still works exactly as
    before for "log out everywhere" (password change/reset).
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    device_info = Column(String(255), nullable=True)   # parsed from User-Agent, e.g. "Chrome on Windows"
    ip_address = Column(String(45), nullable=True)      # IPv4 or IPv6

    is_active = Column(Boolean, nullable=False, default=True, index=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    last_active_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
