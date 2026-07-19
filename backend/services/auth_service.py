"""
Auth services- business logic, kept separate from the router  (routers stay thin).
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.config import settings
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_verification_token,
)
from backend.models.user import User
from backend.schemas.user import UserRegister
from backend.services.category_service import seed_default_categories

def register_user(db: Session, user_data: UserRegister) -> User:
    """
    Create a new user with a hashed password and an email verification token.
    The user is NOT verified yet - is_verified stays False until they click the link.
    Also seeds the default expense/income categories for the new user.
    Raise value error if email is taken.
    """
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ValueError("Email is already registered")
    token = generate_verification_token()
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
    )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash =  hash_password(user_data.password),
        phone=user_data.phone,
        is_verified=False,
        verification_token=token,
        verification_token_expires=expires,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    seed_default_categories(db, new_user.user_id)
    return new_user

def verify_user_email(db: Session, token: str) -> User:
    """
    Verify a user's email using the token from the emailed link.
    Raise ValueError if the token is invalid or expired.
    """
    user = db.query(User).filter(User.verification_token==token).first()
    if not user:
        raise ValueError("Invalid or Expired verification link")
    if user.is_verified:
        return user      #already verified nothing to do
    expires_at = user.verification_token_expires
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)
    if expires_at is None or datetime.now(timezone.utc) > expires_at:
        raise ValueError("Invalid or expired verification link")
    
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires =  None
    db.commit()
    db.refresh(user)
    return user

def resend_verification_token(db: Session, email: str) -> User:
    """
    Generate a fresh verification token for the user who never verified.
    Raises ValueError if user doesn't exist or is already verified.
    """
    user = db.query(User).filter(User.email==email).first()
    if not user:
        raise ValueError("No account found with this email")
    if user.is_verified:
        raise ValueError("This account is already verified")
    
    user.verification_token = generate_verification_token()
    user.verification_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
    )
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Verified credentials and check that the email is verified.
    Raise ValueError with a specific message for each failure case -
    the router decides the right HTTP status code for each.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("INVALID_CREDENTIALS")
    
    if not user.is_verified:
        raise ValueError("EMAIL_NOT_VERIFIED")

    return user


def create_token_for_user(user: User) -> str:
    """
    Create a signed JWT for a given user, embedding their user_id as `sub`
    and their current token_version as `tv`.
    If the user later resets their password, token_version is bumped,
    which makes any JWT signed with the old `tv` invalid immediately -
    even though the JWT itself hasn't technically expired.
    """
    return create_access_token(data={"sub": str(user.user_id), "tv": user.token_version})


def request_password_reset(db: Session, email: str) -> User | None:
    """
    Generate a password reset token for the given email.
    Returns None if no account exists - the router treats this the same as
    success in its response, so we don't leak which emails are registered.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    user.reset_token = generate_verification_token()
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
    """
    Change the logged-in user's password after verifying their current one.
    Bumps token_version (invalidating tokens on other devices/sessions) - the
    router issues a fresh token immediately so the current session keeps working.
    Raises ValueError if the current password is wrong.
    """
    if not verify_password(current_password, user.password_hash):
        raise ValueError("Current password is incorrect")

    user.password_hash = hash_password(new_password)
    user.token_version += 1
    db.commit()
    db.refresh(user)
    return user


def reset_password(db: Session, token: str, new_password: str) -> User:
    """
    Reset a user's password using a valid reset token.
    Bumps token_version, which invalidates every JWT issued before this point.
    Raises ValueError if the token is invalid or expired.
    """
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise ValueError("Invalid or expired reset link")

    expires_at = user.reset_token_expires
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at is None or datetime.now(timezone.utc) > expires_at:
        raise ValueError("Invalid or expired reset link")

    user.password_hash = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.token_version += 1  # invalidates all previously issued JWTs

    db.commit()
    db.refresh(user)
    return user

