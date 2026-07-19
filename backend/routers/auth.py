""""
API routes: register, verify email, resend verification, login, get/update profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import (
    UserRegister,
    UserResponse,
    RegisterResponse,
    MessageResponse,
    TokenResponse,
    UserProfileUpdate,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
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
)
from backend.services.email_service import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


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

    try:
        send_verification_email(user.email, user.name, user.verification_token)
    except Exception:
        # Registration already succeeded in the DB; don't fail the request just
        # because the email didn't send - let the user request a resend instead.
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not send verification email. Please try again shortly.",
        )

    return MessageResponse(message="Verification email sent. Please check your inbox.")


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login using email + password.
    Blocks login with a 403 if the account exists but hasn't verified its email yet.
    Uses OAuth2PasswordRequestForm so it works directly with FastAPI's /docs
    "Authorize" button (it sends `username` + `password` as form fields;
    we treat `username` as the email).
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token_for_user(user)
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
    db: Session = Depends(get_db),
):
    """
    Change the logged-in user's password (requires the current password).
    Invalidates tokens on other devices, but immediately issues a fresh token
    for this session so the user isn't logged out here.
    """
    try:
        user = change_password(db, current_user, payload.current_password, payload.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    access_token = create_token_for_user(user)
    return TokenResponse(access_token=access_token, user=user)

