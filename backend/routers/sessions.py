"""
API routes for session management - list active logins, revoke one,
or revoke every session except the one you're currently using.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import AuthContext, get_current_auth
from backend.database import get_db
from backend.schemas.session import SessionResponse, RevokeOthersResponse
from backend.services.session_service import (
    list_sessions as list_active_sessions,
    revoke_session,
    revoke_all_sessions,
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=list[SessionResponse])
def list_sessions(
    auth: AuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
):
    """List every active (non-revoked) session for the logged-in user, most recently active first."""
    sessions = list_active_sessions(db, auth.user.user_id)
    return [
        SessionResponse.model_validate(s).model_copy(update={"is_current": s.session_id == auth.session_id})
        for s in sessions
    ]


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_one_session(
    session_id: int,
    auth: AuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
):
    """
    Revoke a single session. If it's the session you're currently making
    this request with, you'll be logged out immediately - the frontend
    should clear its stored token when it revokes its own current session.
    """
    revoked = revoke_session(db, auth.user.user_id, session_id)
    if revoked is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


@router.post("/revoke-others", response_model=RevokeOthersResponse)
def revoke_others(
    auth: AuthContext = Depends(get_current_auth),
    db: Session = Depends(get_db),
):
    """Log out every other device/session, keeping the current one active."""
    count = revoke_all_sessions(db, auth.user.user_id, except_session_id=auth.session_id)
    return RevokeOthersResponse(revoked_count=count)
