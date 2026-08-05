"""
Alert & Notification System - Milestone 3

This service is the shared foundation the other two M3 slices build on top
of:
  - AI Insights (spending analysis / recommendations / health score) calls
    create_notification() when something worth surfacing happens (a new
    recommendation, a health score drop, etc.)
  - Reports doesn't need to call this directly, but may in future (e.g.
    "your monthly report is ready").

FROZEN CONTRACT - do not change this signature without telling the whole
team, since other services are written against it:

    create_notification(db: Session, user_id: int, title: str,
                         message: str, type: str = "system") -> Notification

`type` is a free string by design (not a DB enum) so new notification
categories can be introduced by any teammate without a migration. Stick to
short, lowercase, singular words where possible - e.g. "budget",
"investment", "goal", "system" - for consistency in the UI, but nothing
enforces this.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    type: str = "system",
    action_url: str | None = None,
) -> Notification:
    """
    Creates and persists a single in-app notification for a user.
    Call this from anywhere in the codebase - event hooks in other services,
    or scheduled jobs - whenever something happens that the user should be
    told about.

    action_url is an optional frontend route (e.g. "/financial-health") that
    the notification should open when clicked - leave it None for
    notifications with nothing specific to link to.
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        action_url=action_url,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50,
) -> list[Notification]:
    """Most recent notifications first."""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)  # noqa: E712
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def get_unread_count(db: Session, user_id: int) -> int:
    return (
        db.query(func.count(Notification.notification_id))
        .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .scalar()
        or 0
    )


def mark_as_read(db: Session, user_id: int, notification_id: int) -> Notification | None:
    """Returns None if no matching notification exists for this user (caller should 404)."""
    notification = (
        db.query(Notification)
        .filter(Notification.notification_id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if notification is None:
        return None

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user_id: int) -> int:
    """Returns the count of notifications marked read."""
    updated_count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return updated_count
