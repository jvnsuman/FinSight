"""
UserSession ORM model - one row per issued JWT ("session"/device login).

Lets us do real session management: list every device a user is logged in
on, revoke one specific session, or revoke all-but-the-current-one - instead
of the old all-or-nothing token_version kill switch (which still exists and
still works as a hard global kill for password changes/resets/deletion).

session_id doubles as the JWT's `jti` claim - get_current_user looks the
token's jti up here on every request to check it hasn't been individually
revoked, even if the token itself hasn't expired yet.
"""
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id = Column(String(43), primary_key=True)  # secrets.token_urlsafe(32) output length
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)

    # Best-effort, human-readable device label parsed from the User-Agent
    # header at login time (e.g. "Chrome on Windows"). Cosmetic only - never
    # used for any security decision.
    device_label = Column(String(150), nullable=True)
    ip_address = Column(String(45), nullable=True)  # long enough for IPv6

    revoked = Column(Boolean, nullable=False, default=False, server_default="false")
    revoked_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    last_active_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sessions")
