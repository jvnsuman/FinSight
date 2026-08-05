"""
Part 1: User Authentication & Profile
Shared FastAPI dependencies - primarily `get_current_user`, used to protect routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.core.security import decode_access_token
from backend.database import get_db
from backend.models.user import User
from backend.services.session_service import is_session_active, touch_session

# Tells FastAPI's docs where to send the login request to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user (
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    Decodes the JWT from the Authorization header, fetches the matching user.
    Raises 401 if the token is missing, invalid, expired, the user no longer
    exists, or the specific session this token belongs to has been revoked
    (logged out remotely from another device - Milestone 3 session management).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    token_version = payload.get("tv")
    session_id = payload.get("sid")
    if user_id is None or token_version is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    # Deactivation already revokes every session (see auth_service.
    # deactivate_account), so this mainly matters for tokens issued before
    # the `sid` claim existed - deactivated users shouldn't be able to keep
    # using those regardless of session state.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # If the password was reset since this token was issued, token_version on the user 
    # will have incremented past what's embedded in this JWT - reject it.
    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired due to a password change. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Tokens issued before this feature existed have no `sid` claim - treat
    # them as valid rather than locking out every pre-existing session; new
    # logins always carry a sid going forward.
    if session_id is not None:
        if not is_session_active(db, int(session_id)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This session has been logged out from another device. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        touch_session(db, int(session_id))

    return user


def get_current_session_id(token: str = Depends(oauth2_scheme)) -> int | None:
    """
    Extracts just the `sid` claim from the current request's JWT, without
    re-validating the whole session (get_current_user already does that in
    the same request). Used by endpoints like change-password that need to
    reissue a token for the SAME session rather than creating a new one.
    Returns None for older tokens issued before this feature existed.
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    session_id = payload.get("sid")
    return int(session_id) if session_id is not None else None
