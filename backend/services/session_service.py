"""
Session Management service - login tracking, in-app + email login alerts,
and selective per-device logout.

This is the piece that makes "log out just that one device" possible: unlike
`token_version` (which invalidates every JWT for a user at once), each login
gets its own `UserSession` row, and each JWT embeds that row's `session_id`
as the `sid` claim. Revoking one session flips only that row's `is_active`
to False - `get_current_user` rejects the token on its next use, while every
other active session for the user keeps working untouched.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.config import settings
from backend.core.security import generate_verification_token
from backend.models.user import User
from backend.models.user_session import UserSession
from backend.services.notification_service import create_notification
from backend.services.email_service import send_login_alert_email


def create_session(
    db: Session,
    user: User,
    device_info: str | None,
    ip_address: str | None,
) -> UserSession:
    """
    Called right after successful credential verification, before issuing
    the JWT. Creates the session row, fires an in-app notification, and
    sends a login-alert email (which includes a "reset your password" link,
    in case this login wasn't the account owner). Email failures are
    swallowed here (same pattern as elsewhere in the app - login should not
    fail just because SMTP hiccuped); the in-app notification is the
    reliable fallback.
    """
    session = UserSession(
        user_id=user.user_id,
        device_info=device_info,
        ip_address=ip_address,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    location_bit = f" from {ip_address}" if ip_address else ""
    create_notification(
        db=db,
        user_id=user.user_id,
        title="New login detected",
        message=f"A new login to your account was detected on {device_info or 'an unknown device'}{location_bit}.",
        type="security",
        action_url="/profile#sessions",
    )

    # Reuses the same reset_token/reset_token_expires fields on User that
    # /auth/forgot-password uses - this IS a real, valid reset link, not a
    # separate mechanism. Generated inline here (rather than importing
    # auth_service.request_password_reset) to avoid a circular import:
    # auth_service will need to call INTO this module (revoke_all_sessions)
    # once password reset is wired to log out other devices.
    user.reset_token = generate_verification_token()
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    db.commit()
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={user.reset_token}"

    try:
        send_login_alert_email(user.email, user.name, device_info, ip_address, reset_link=reset_link)
    except Exception:
        pass  # in-app notification above already covers this; don't block login on SMTP issues

    return session


def is_session_active(db: Session, session_id: int) -> bool:
    session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
    return session is not None and session.is_active


def list_sessions(db: Session, user_id: int) -> list[UserSession]:
    """Most recently active first."""
    return (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.is_active == True)  # noqa: E712
        .order_by(UserSession.last_active_at.desc())
        .all()
    )


def revoke_session(db: Session, user_id: int, session_id: int) -> UserSession | None:
    """
    Logs out one specific device. Returns None if no matching active session
    exists for this user (caller should 404) - deliberately scoped to
    user_id so one user can never revoke another user's session.
    """
    session = (
        db.query(UserSession)
        .filter(UserSession.session_id == session_id, UserSession.user_id == user_id)
        .first()
    )
    if session is None:
        return None

    session.is_active = False
    db.commit()
    db.refresh(session)
    return session


def revoke_all_sessions(db: Session, user_id: int, except_session_id: int | None = None) -> int:
    """
    Logs out every active session for a user - used after a password reset,
    since that's the account owner regaining control and every other device
    (potentially an attacker's) should be kicked out immediately.

    `except_session_id` is accepted for future use (e.g. keeping the device
    that performed the reset logged in) but password-reset today always
    passes None, since the user isn't authenticated yet at that point -
    they're using an emailed token, not an existing session - so there's no
    "current" session to preserve.

    Returns the count of sessions revoked.
    """
    query = db.query(UserSession).filter(UserSession.user_id == user_id, UserSession.is_active == True)  # noqa: E712
    if except_session_id is not None:
        query = query.filter(UserSession.session_id != except_session_id)

    count = query.update({"is_active": False}, synchronize_session=False)
    db.commit()
    return count


def touch_session(db: Session, session_id: int) -> None:
    """
    Bumps last_active_at to now - called on each authenticated request
    (from get_current_user) so the session list reflects genuinely recent
    activity, not just the moment the user logged in.
    """
    db.query(UserSession).filter(UserSession.session_id == session_id).update(
        {"last_active_at": datetime.now(timezone.utc)}
    )
    db.commit()
