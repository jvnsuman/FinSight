from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
import json

from backend.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.services import financial_health_service

router = APIRouter(prefix="/api/financial-health", tags=["Financial Health"])

class SimulationRequest(BaseModel):
    overrides: Dict[str, float]
    skip_ai: bool = False

class AskCoachRequest(BaseModel):
    question: str

@router.get("/")
def get_financial_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cache = financial_health_service.get_or_update_health_cache(db, current_user.user_id)
        return {
            "score": cache.score,
            "metrics": cache.metrics_json,
            "insights": cache.ai_insights_json,
            "last_updated": cache.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving financial health: {str(e)}"
        )

@router.post("/refresh")
def refresh_financial_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cache = financial_health_service.get_or_update_health_cache(db, current_user.user_id, force_refresh=True)
        return {
            "score": cache.score,
            "metrics": cache.metrics_json,
            "insights": cache.ai_insights_json,
            "last_updated": cache.updated_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing financial health: {str(e)}"
        )

@router.post("/simulate")
def simulate_financial_health(
    request: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = financial_health_service.simulate_score(db, current_user.user_id, request.overrides, request.skip_ai)
        return {
            "score": result["score"],
            "metrics": result["metrics_json"],
            "insights": result["ai_insights_json"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error simulating financial health: {str(e)}"
        )

@router.post("/ask")
def ask_health_coach(
    request: AskCoachRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        cache = financial_health_service.get_or_update_health_cache(db, current_user.user_id)
        
        context = {
            "financial_score": cache.score,
            "metrics": cache.metrics_json,
            "insights": cache.ai_insights_json
        }
        
        prompt = f"""
        You are an expert AI Financial Coach for this user.
        The user has asked: "{request.question}"
        
        Here are the user's current aggregated financial health metrics and insights:
        {json.dumps(context, indent=2)}
        
        Answer the user's question directly, clearly, and concisely (max 3-4 sentences).
        Base your answer ONLY on the provided metrics and insights.
        """
        
        response = financial_health_service._client.models.generate_content(
            model=financial_health_service._GEMINI_MODEL, contents=prompt
        )

        return {"answer": response.text.strip()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error asking AI coach: {str(e)}"
        )
