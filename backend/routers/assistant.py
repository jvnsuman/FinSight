from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.assistant import AssistantQuery, AssistantResponse
from backend.services.assistant_service import handle_query

router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"]
)

@router.post("/query", response_model=AssistantResponse)
def query_assistant(
    request: AssistantQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query the AI assistant. 
    Requires authentication to safely pass user context to the RAG pipeline.
    """
    answer_text, mode_used = handle_query(db, current_user, request.query)
    
    return AssistantResponse(
        answer=answer_text,
        mode_used=mode_used
    )
