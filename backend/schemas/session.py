"""
Pydantic schemas for session management (login alerts + selective device logout).
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    session_id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    last_active_at: datetime
    is_current: bool = False  # True for the session making this very request

    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]


class RevokeSessionResponse(BaseModel):
    session_id: int
    revoked: bool


class RevokeOthersResponse(BaseModel):
    revoked_count: int
