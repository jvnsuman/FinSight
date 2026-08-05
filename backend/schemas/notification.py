"""
Pydantic schemas for Notification.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NotificationCreate(BaseModel):
    """
    Internal-use schema - not exposed on a router. This is what
    notification_service.create_notification() accepts, mirrored here so the
    other two M3 slices (AI insights, reports) can see the exact shape they're
    expected to call with.
    """
    user_id: int
    title: str = Field(min_length=1, max_length=150)
    message: str = Field(min_length=1, max_length=500)
    type: str = Field(default="system", max_length=50)
    action_url: Optional[str] = Field(default=None, max_length=255)


class NotificationResponse(BaseModel):
    notification_id: int
    title: str
    message: str
    type: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int


class MarkReadResponse(BaseModel):
    notification_id: int
    is_read: bool


class MarkAllReadResponse(BaseModel):
    marked_count: int
