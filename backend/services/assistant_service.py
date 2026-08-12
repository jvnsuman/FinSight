import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc
from google import genai

from backend.config import settings
from backend.models.user import User
from backend.models.account import Account
from backend.models.transaction import Transaction
from backend.models.budget import Budget
from backend.models.goal import Goal
from backend.models.investment import Investment
from backend.models.trade import Trade

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-flash-latest"

# Build the client once at module load, the same way the old SDK's
# genai.configure() was called once. A missing key still doesn't raise
# here - handle_query() checks settings.GEMINI_API_KEY itself before ever
# calling the model, matching the old behavior.
_client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None
if not settings.GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set. Assistant will fail on use.")

def _detect_intent(query: str) -> str:
    """
    Detects whether the query is related to personal finance or general knowledge.
    """
    prompt = (
        "Classify the following user query into exactly one of two categories: 'personal' or 'general'.\n"
        "- 'personal': The user is asking about their own financial data, spending, budget, portfolio, accounts, transactions, investments, or asking to analyze their data.\n"
        "- 'general': The user is asking a general knowledge question (e.g., 'What is SIP?', 'Explain inflation', 'Teach me Python', 'How do mutual funds work?').\n"
        "Return strictly the word 'personal' or 'general' and nothing else.\n\n"
        f"Query: {query}"
    )
    response = _client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
    classification = response.text.strip().lower()
    if "personal" in classification:
        return "personal"
    return "general"

def handle_query(db: Session, user: User, query: str) -> tuple[str, str]:
    """
    Handles a user query by detecting intent and routing to Gemini.
    Returns (answer_text, mode_used).
    """
    if not settings.GEMINI_API_KEY:
        return "Error: Gemini API key is not configured on the server.", "general"
        
    try:
        mode = _detect_intent(query)
        if mode == "personal":
            return _handle_personal_query(db, user, query), "personal"
        else:
            return _handle_general_query(query), "general"
    except Exception as e:
        logger.error(f"Error in assistant service: {str(e)}")
        return f"I encountered an error processing your request. Details: {str(e)}", "general"

def _handle_general_query(query: str) -> str:
    """
    Handles general knowledge queries using Gemini flash without personal data context.
    """
    prompt = f"You are Finance Analytics Platform's helpful financial assistant. Answer this query in a general context: {query}"

    response = _client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
    return response.text

def _handle_personal_query(db: Session, user: User, query: str) -> str:
    """
    Handles queries requiring user financial context. 
    Retrieves a bounded set of recent data to keep latency low and strictly
    scopes it to the user.
    """
    # 1. Gather context data strictly scoped to this user
    
    # Get active accounts
    accounts = db.query(Account).filter(Account.user_id == user.user_id, Account.is_active == True).all()
    account_summary = []
    for acc in accounts:
        # Data masking: ensure account number is masked if it's longer than 4 chars
        acct_num = acc.account_number or "N/A"
        if len(acct_num) > 4:
            acct_num = f"****{acct_num[-4:]}"
            
        account_summary.append({
            "name": acc.account_name,
            "type": acc.account_type,
            "bank": acc.bank_name,
            "account_ending": acct_num,
            "balance": float(acc.balance)
        })
        
    # Get recent transactions (limit to 50 for low latency/prompt size)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.user_id)
        .order_by(desc(Transaction.transaction_date))
        .limit(50)
        .all()
    )
    
    txn_summary = []
    for txn in transactions:
        txn_summary.append({
            "date": txn.transaction_date.isoformat(),
            "type": txn.transaction_type,
            "amount": float(txn.amount),
            "description": txn.description or "",
            "category": txn.category.category_name if txn.category else "Uncategorized"
        })

    # Get active budgets
    budgets = db.query(Budget).filter(Budget.user_id == user.user_id).all()
    budget_summary = []
    for b in budgets:
        budget_summary.append({
            "amount": float(b.amount),
            "month": b.month.isoformat(),
            "category": b.category.category_name if b.category else "Overall"
        })

    # Get active goals
    goals = db.query(Goal).filter(Goal.user_id == user.user_id).all()
    goal_summary = []
    for g in goals:
        goal_summary.append({
            "name": g.goal_name,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "target_date": g.target_date.isoformat(),
            "status": g.status
        })

    # Get active investments
    investments = db.query(Investment).filter(Investment.user_id == user.user_id, Investment.is_active == True).all()
    investment_summary = []
    for i in investments:
        investment_summary.append({
            "asset_name": i.asset_name,
            "asset_type": i.asset_type,
            "symbol": i.symbol or "",
            "quantity": float(i.quantity),
            "purchase_price": float(i.purchase_price)
        })

    # Get recent trades (limit to 30)
    trades = (
        db.query(Trade)
        .filter(Trade.user_id == user.user_id)
        .order_by(desc(Trade.trade_date))
        .limit(30)
        .all()
    )
    trade_summary = []
    for t in trades:
        trade_summary.append({
            "action": t.action,
            "asset": t.asset_name or t.asset_type,
            "quantity": float(t.quantity) if t.quantity else 0.0,
            "cash_amount": float(t.cash_amount),
            "date": t.trade_date.isoformat()
        })

    # 2. Build the context string
    context_data = {
        "accounts": account_summary,
        "recent_transactions_limit_50": txn_summary,
        "budgets": budget_summary,
        "goals": goal_summary,
        "investments": investment_summary,
        "recent_trades_limit_30": trade_summary
    }
    
    context_json = json.dumps(context_data, indent=2)

    # 3. Construct the strict prompt
    system_instruction = (
        "You are Finance Analytics Platform's secure AI financial assistant. You are provided with a specific user's "
        "accurate, real-time financial data as JSON context (accounts, transactions, budgets, goals, investments, trades). "
        "Your task is to answer the user's query based STRICTLY on this provided context. "
        "Do NOT invent, guess, or use dummy values. If the answer cannot be derived from the provided context, "
        "state that you do not have enough information.\n\n"
        "FORMATTING RULES:\n"
        "- Use Markdown formatting heavily to make your response beautiful and easy to read.\n"
        "- Use Markdown tables when listing multiple transactions, accounts, or goals.\n"
        "- Use **bold text** for important numbers or key takeaways.\n"
        "- Be concise, helpful, and highly professional."
    )
    
    prompt = f"{system_instruction}\n\nContext Data:\n```json\n{context_json}\n```\n\nUser Query: {query}"
    
    # 4. Generate response using the fast flash model
    response = _client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)

    return response.text
