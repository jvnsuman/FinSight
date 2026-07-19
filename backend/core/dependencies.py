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

# Tells FastAPI's docs where to send the login request to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user (
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    Decodes the JWT from the Authorization header, fetches the matching user.
    Raises 401 if the token is missing, invalid, expired, or the user no longer exists.
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
    if user_id is None or token_version is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    # If the password was reset since this token was issued, token_version on the user 
    # will have incremented past what's embedded in this JWT - reject it.
    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired due to a password change. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
