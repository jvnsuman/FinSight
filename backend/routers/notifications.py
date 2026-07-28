"""
API routers for the in-app alert & notification system (Milestone 3).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    MarkReadResponse,
    MarkAllReadResponse,
)
from backend.services.notification_service import (
    list_notifications,
    get_unread_count,
    mark_as_read,
    mark_all_as_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's notifications, most recent first."""
    notifications = list_notifications(db, current_user.user_id, unread_only=unread_only, limit=limit)
    unread_count = get_unread_count(db, current_user.user_id)
    return NotificationListResponse(notifications=notifications, unread_count=unread_count)


@router.get("/unread-count")
def get_unread_count_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lightweight endpoint for polling a badge count without fetching the full list."""
    return {"unread_count": get_unread_count(db, current_user.user_id)}


@router.patch("/{notification_id}/read", response_model=MarkReadResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a single notification as read."""
    notification = mark_as_read(db, current_user.user_id, notification_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return MarkReadResponse(notification_id=notification.notification_id, is_read=notification.is_read)


@router.patch("/read-all", response_model=MarkAllReadResponse)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark all of the current user's unread notifications as read."""
    count = mark_all_as_read(db, current_user.user_id)
    return MarkAllReadResponse(marked_count=count)
