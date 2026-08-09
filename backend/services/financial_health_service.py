import json
import traceback
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from google import genai

from backend.config import settings
from backend.models.financial_health import FinancialHealthCache
from backend.models.transaction import Transaction
from backend.models.budget import Budget
from backend.models.account import Account
from backend.models.goal import Goal
from backend.models.investment import Investment

_GEMINI_MODEL = "gemini-flash-latest"

# Built once at module load, same as the old genai.configure() call. Left
# as None on any failure (e.g. missing key) - callers already wrap their
# generate_content call in try/except and fall back to a default response,
# so a None client surfaces the same way a misconfigured old-SDK call did.
try:
    _client = genai.Client(api_key=settings.GEMINI_API_KEY)
except Exception:
    _client = None

DEFAULT_WEIGHTS = {
    "savings_rate": 20,
    "budget_discipline": 20,
    "emergency_fund": 15,
    "investment_habit": 15,
    "expense_stability": 10,
    "goal_progress": 10,
    "debt_management": 10
}

def _calculate_savings_rate(db: Session, user_id: int, start_date: date) -> float:
    # (Income - Expense) / Income over last 90 days
    totals = db.query(
        Transaction.transaction_type, 
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_type.in_(["income", "expense"])
    ).group_by(Transaction.transaction_type).all()
    
    income = 0.0
    expense = 0.0
    for t_type, total in totals:
        if t_type == "income":
            income = float(total or 0)
        elif t_type == "expense":
            expense = float(total or 0)
            
    if income == 0:
        return 0.0
    
    rate = ((income - expense) / income) * 100.0
    return max(0.0, min(100.0, rate)) # clamp 0-100

def _calculate_budget_discipline(db: Session, user_id: int) -> float:
    # For all budgets in current month, average (spent / amount)
    today = date.today()
    first_of_month = today.replace(day=1)
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == first_of_month
    ).all()
    
    if not budgets:
        return 100.0 # No budgets set means no overspending? Or maybe N/A, but we return 100 as neutral.
        
    total_spent_ratio = 0.0
    valid_budgets = 0
    for b in budgets:
        # Sum expenses for this budget category (or all if category_id is None)
        query = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "expense",
            Transaction.transaction_date >= first_of_month
        )
        if b.category_id:
            query = query.filter(Transaction.category_id == b.category_id)
            
        spent = float(query.scalar() or 0.0)
        limit = float(b.amount or 1.0)
        ratio = spent / limit if limit > 0 else 1.0
        
        # Calculate a sub-score (0 if over budget, 100 if under)
        # E.g. spent 50%, score 100. Spent 110%, score 0.
        sub_score = max(0.0, 100.0 - ((ratio - 1.0) * 100.0) if ratio > 1.0 else 100.0)
        total_spent_ratio += sub_score
        valid_budgets += 1
        
    if valid_budgets == 0:
        return 100.0
    return total_spent_ratio / valid_budgets

def _calculate_emergency_fund(db: Session, user_id: int, start_date: date) -> float:
    # Total bank/wallet balance / avg monthly expenses
    total_liquid = db.query(func.sum(Account.balance)).filter(
        Account.user_id == user_id,
        Account.account_type.in_(["bank", "wallet"])
    ).scalar() or 0.0
    total_liquid = float(total_liquid)
    
    # 90 days expenses = 3 months
    expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "expense",
        Transaction.transaction_date >= start_date
    ).scalar() or 0.0
    
    monthly_expenses = float(expenses) / 3.0
    if monthly_expenses == 0:
        return 100.0 if total_liquid > 0 else 0.0
        
    months_covered = total_liquid / monthly_expenses
    # Score: 6 months = 100
    score = (months_covered / 6.0) * 100.0
    return max(0.0, min(100.0, score))

def _calculate_investment_habit(db: Session, user_id: int, start_date: date) -> float:
    # Ratio of investments to income
    investments = db.query(func.sum(Investment.quantity * Investment.purchase_price)).filter(
        Investment.user_id == user_id,
        Investment.purchase_date >= start_date
    ).scalar() or 0.0
    
    income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "income",
        Transaction.transaction_date >= start_date
    ).scalar() or 0.0
    
    if float(income) == 0:
        return 0.0
        
    ratio = float(investments) / float(income)
    # E.g. investing 20% of income = 100 score
    score = (ratio / 0.20) * 100.0
    return max(0.0, min(100.0, score))

def _calculate_expense_stability(db: Session, user_id: int) -> float:
    # (Just an approximation: standard deviation is complex in ORM, we'll do something simple)
    # We will just return a placeholder or an average. 80 is a good default if we can't calculate variance.
    return 80.0

def _calculate_goal_progress(db: Session, user_id: int) -> float:
    goals = db.query(Goal).filter(Goal.user_id == user_id, Goal.status == "on_track").all()
    if not goals:
        return -1.0 # Means N/A
        
    total_score = 0.0
    for g in goals:
        cur = float(g.current_amount or 0.0)
        tgt = float(g.target_amount or 1.0)
        ratio = (cur / tgt) * 100.0
        total_score += max(0.0, min(100.0, ratio))
    return total_score / len(goals)

def _calculate_debt_management(db: Session, user_id: int) -> float:
    # Negative balance in credit cards
    credit_cards = db.query(Account).filter(
        Account.user_id == user_id,
        Account.account_type == "card"
    ).all()
    
    if not credit_cards:
        return -1.0 # N/A
        
    total_debt = sum([abs(float(c.balance)) for c in credit_cards if float(c.balance) < 0])
    # Simple logic: 0 debt = 100. High debt reduces score.
    # We don't have income in this function directly, so we just use an arbitrary scale for MVP.
    # Real app would use DTI ratio.
    if total_debt == 0:
        return 100.0
    return 50.0 # Default if there is some debt but we don't have DTI

def calculate_raw_metrics(db: Session, user_id: int, overrides: Dict[str, Any] = None) -> Dict[str, float]:
    start_date = date.today() - timedelta(days=90)
    
    metrics = {
        "savings_rate": _calculate_savings_rate(db, user_id, start_date),
        "budget_discipline": _calculate_budget_discipline(db, user_id),
        "emergency_fund": _calculate_emergency_fund(db, user_id, start_date),
        "investment_habit": _calculate_investment_habit(db, user_id, start_date),
        "expense_stability": _calculate_expense_stability(db, user_id),
        "goal_progress": _calculate_goal_progress(db, user_id),
        "debt_management": _calculate_debt_management(db, user_id)
    }
    
    if overrides:
        for k, v in overrides.items():
            if k in metrics:
                metrics[k] = float(v)
                
    return metrics

def compute_overall_score(metrics: Dict[str, float]) -> int:
    weights = DEFAULT_WEIGHTS.copy()
    
    # If N/A (-1.0), redistribute weights
    active_weights = 0.0
    for k, v in metrics.items():
        if v >= 0:
            active_weights += weights[k]
            
    if active_weights == 0:
        return 0
        
    total_score = 0.0
    for k, v in metrics.items():
        if v >= 0:
            normalized_weight = weights[k] / active_weights
            total_score += v * normalized_weight
            
    return int(round(total_score))

def _get_health_category(score: int) -> str:
    if score >= 90: return "Excellent"
    if score >= 75: return "Very Good"
    if score >= 60: return "Good"
    if score >= 40: return "Needs Improvement"
    return "Financially At Risk"

def generate_ai_insights(metrics: Dict[str, float], score: int) -> Dict[str, Any]:
    context = {
        "financial_score": score,
        "score_category": _get_health_category(score),
        "metrics": metrics
    }
    
    prompt = f"""
    You are an expert AI Financial Coach. Analyze this user's aggregated financial health metrics.
    NEVER reference personal data, just the metrics provided.
    
    Metrics:
    {json.dumps(context, indent=2)}
    
    Return a strictly valid JSON object with the following keys exactly:
    - "explanation": string (A brief 1-2 sentence explanation of why they received this score).
    - "strengths": array of strings (Identify 2-3 positive financial habits).
    - "weaknesses": array of strings (Identify 1-2 areas reducing the score).
    - "recommendations": array of strings (Provide 2-3 practical recommendations based on metrics).
    - "action_plan": array of strings (Short, achievable goals for this month).
    
    Respond ONLY with raw valid JSON. Do not use markdown blocks like ```json.
    """
    
    try:
        response = _client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return {
            "explanation": "Unable to generate AI insights at this time.",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "action_plan": []
        }

def get_or_update_health_cache(db: Session, user_id: int, force_refresh: bool = False) -> FinancialHealthCache:
    cache = db.query(FinancialHealthCache).filter(FinancialHealthCache.user_id == user_id).first()
    
    # Refresh if no cache or older than 24h or forced
    if force_refresh or not cache or not cache.updated_at or (datetime.utcnow() - cache.updated_at).total_seconds() > 86400:
        old_score = cache.score if cache else None

        metrics = calculate_raw_metrics(db, user_id)
        score = compute_overall_score(metrics)
        insights = generate_ai_insights(metrics, score)
        
        if not cache:
            cache = FinancialHealthCache(
                user_id=user_id,
                score=score,
                metrics_json=metrics,
                ai_insights_json=insights
            )
            db.add(cache)
        else:
            cache.score = score
            cache.metrics_json = metrics
            cache.ai_insights_json = insights
            
        db.commit()
        db.refresh(cache)

        # Local import to avoid a circular import at module load time (same
        # convention as transaction_service -> savings_service).
        from backend.services.alert_service import check_health_score_status
        check_health_score_status(db, user_id, old_score, score, _get_health_category(score))

    return cache

def simulate_score(db: Session, user_id: int, overrides: Dict[str, Any], skip_ai: bool = False) -> Dict[str, Any]:
    metrics = calculate_raw_metrics(db, user_id, overrides)
    score = compute_overall_score(metrics)
    
    insights = None
    if not skip_ai:
        insights = generate_ai_insights(metrics, score)
        
    return {
        "score": score,
        "metrics_json": metrics,
        "ai_insights_json": insights
    }
