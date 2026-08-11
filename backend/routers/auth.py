""""
API routes: register, verify email, resend verification, login, get/update profile.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user, get_current_session_id
from backend.core.security import parse_device_info
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import (
    UserRegister,
    UserResponse,
    RegisterResponse,
    MessageResponse,
    VerificationStatusResponse,
    TokenResponse,
    UserProfileUpdate,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    DeactivateAccountRequest,
    DeactivateAccountResponse,
)
from backend.services.auth_service import (
    register_user,
    authenticate_user,
    create_token_for_user,
    verify_user_email,
    resend_verification_token,
    request_password_reset,
    reset_password,
    change_password,
    deactivate_account,
    DEACTIVATION_GRACE_PERIOD_DAYS,
)
from backend.services.email_service import send_verification_email, send_password_reset_email
from backend.services.session_service import create_session, list_sessions, revoke_session
from backend.schemas.session import SessionResponse, SessionListResponse, RevokeSessionResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account. The account is created but NOT verified.
    A verification link is emailed to the user; they must click it before they can log in.
    """
    try:
        user = register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    print(f"[EMAIL DIAGNOSTIC] register_user succeeded for {user.email!r}, "
          f"about to call send_verification_email", flush=True)

    try:
        send_verification_email(user.email, user.name, user.verification_token)
    except Exception:
        # Registration already succeeded in the DB; don't fail the request just
        # because the email didn't send - let the user request a resend instead.
        # Logged with the full traceback (exc_info=True) because this was
        # previously a bare "except Exception: raise HTTPException(...)" that
        # discarded the real SMTP error entirely - impossible to tell an auth
        # failure from a wrong host from a network timeout without this.
        logger.exception("Failed to send verification email to %s", user.email)
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Account created, but the verification email could not be sent. "
                   "Please use /auth/resend-verification to try again.",
        )

    return RegisterResponse(
        message="Registration successful. Please check your email to verify your account.",
        email=user.email,
    )


@router.get("/verify-email", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Called when the user clicks the verification link in their email.
    Example: GET /auth/verify-email?token=abc123
    """
    try:
        verify_user_email(db, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageResponse(message="Email verified successfully. You can now log in.")


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Send a new verification email if the previous link expired or was lost."""
    try:
        user = resend_verification_token(db, payload.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        send_verification_email(user.email, user.name, user.verification_token)
    except Exception:
        logger.exception("Failed to resend verification email to %s", user.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not send verification email. Please try again shortly.",
        )


@router.get("/verification-status", response_model=VerificationStatusResponse)
def verification_status(email: str, db: Session = Depends(get_db)):
    """
    Public, pre-login check of whether an account's email has been
    verified yet - polled by the "check your inbox" page after signup so
    it can auto-log the user in the moment they click the emailed link,
    without them needing to come back and log in manually. Deliberately
    returns only the boolean (never account existence/other fields) so it
    can't be used to enumerate registered emails.
    """
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        # Same response shape as "exists but not verified yet" - don't
        # reveal whether the email is registered at all.
        return VerificationStatusResponse(is_verified=False)
    return VerificationStatusResponse(is_verified=user.is_verified)

    return MessageResponse(message="Verification email sent. Please check your inbox.")


@router.post("/login", response_model=TokenResponse)
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login using email + password.
    Blocks login with a 403 if the account exists but hasn't verified its email yet.
    Uses OAuth2PasswordRequestForm so it works directly with FastAPI's /docs
    "Authorize" button (it sends `username` + `password` as form fields;
    we treat `username` as the email).

    On success, also creates a new session row (Milestone 3 - session
    management), which fires an in-app "new login" notification and sends a
    login-alert email. The user can see and revoke this (or any other)
    session later from GET/DELETE /auth/sessions.
    """
    try:
        user = authenticate_user(db, email=form_data.username, password=form_data.password)
    except ValueError as e:
        if str(e) == "EMAIL_NOT_VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in. "
                       "Use /auth/resend-verification if you need a new link.",
            )
        if str(e) == "ACCOUNT_DEACTIVATED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Contact support if you'd like to reactivate it.",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    device_info = parse_device_info(request.headers.get("user-agent"))
    ip_address = request.client.host if request.client else None
    session = create_session(db, user, device_info, ip_address)

    access_token = create_token_for_user(user, session.session_id)
    return TokenResponse(access_token=access_token, user=user)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset link. Always returns the same success message
    whether or not the email exists, so we don't reveal registered emails.
    """
    user = request_password_reset(db, payload.email)
    if user:
        try:
            send_password_reset_email(user.email, user.name, user.reset_token)
        except Exception:
            logger.exception("Failed to send password reset email to %s", user.email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not send reset email. Please try again shortly.",
            )

    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password_endpoint(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using the token from the emailed link.
    All previously issued JWTs are invalidated immediately (token_version bump) -
    the user must log in again everywhere after this.
    """
    try:
        reset_password(db, payload.token, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return MessageResponse(message="Password reset successful. Please log in with your new password.")


@router.get("/me", response_model=UserResponse)
def read_profile(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user's profile. Requires a valid JWT."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_profile(
    updates: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile fields: name, phone, monthly_income, currency."""
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=TokenResponse)
def change_password_endpoint(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    current_session_id: int | None = Depends(get_current_session_id),
    db: Session = Depends(get_db),
):
    """
    Change the logged-in user's password (requires the current password).
    Invalidates tokens on other devices, but immediately issues a fresh token
    for THIS session (not a new one) so the user isn't logged out here and
    their session doesn't show up twice in their sessions list.
    """
    try:
        user = change_password(db, current_user, payload.current_password, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    access_token = create_token_for_user(user, current_session_id)
    return TokenResponse(access_token=access_token, user=user)


@router.delete("/me", response_model=DeactivateAccountResponse)
def deactivate_account_endpoint(
    payload: DeactivateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deactivate (soft-delete) the logged-in user's own account. Requires the
    current password as confirmation, since this is the most destructive
    self-service action in the app.

    Immediately logs the account out of every device. The account and all
    its data are kept for a 30-day grace period before being permanently
    deleted - contact support during that window to reactivate. A detailed
    confirmation email is sent explaining exactly what happened and what to
    expect next.
    """
    try:
        user = deactivate_account(db, current_user, payload.current_password, payload.reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    purge_date = user.deletion_requested_at + timedelta(days=DEACTIVATION_GRACE_PERIOD_DAYS)
    return DeactivateAccountResponse(
        message=(
            f"Your account has been deactivated and you've been logged out everywhere. "
            f"It will be permanently deleted on {purge_date.strftime('%d %B %Y')} unless you contact "
            f"support before then. A confirmation email has been sent with the full details."
        ),
        deletion_requested_at=user.deletion_requested_at,
        permanent_deletion_date=purge_date,
    )


@router.get("/sessions", response_model=SessionListResponse)
def get_sessions(
    current_user: User = Depends(get_current_user),
    current_session_id: int | None = Depends(get_current_session_id),
    db: Session = Depends(get_db),
):
    """
    List every device currently logged into this account. Lets the user spot
    a session they don't recognize and revoke it with DELETE /auth/sessions/{id}.
    """
    sessions = list_sessions(db, current_user.user_id)
    return SessionListResponse(
        sessions=[
            SessionResponse(
                session_id=s.session_id,
                device_info=s.device_info,
                ip_address=s.ip_address,
                created_at=s.created_at,
                last_active_at=s.last_active_at,
                is_current=(s.session_id == current_session_id),
            )
            for s in sessions
        ]
    )


@router.delete("/sessions/{session_id}", response_model=RevokeSessionResponse)
def revoke_session_endpoint(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Log out one specific device/session - e.g. a session the user doesn't
    recognize from the list returned by GET /auth/sessions. Every other
    active session for this user is left untouched.
    """
    session = revoke_session(db, current_user.user_id, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return RevokeSessionResponse(session_id=session.session_id, revoked=True)

