"""
FinSight - Main Application Entrypoint
========================================
This is the parent file. As we build each of the 4 Milestone 1 parts,
we will import and register their routers here:

  Part 1 - Authentication & Profile   -> backend.routers.auth
  Part 2 - Expense & Transactions     -> backend.routers.accounts, backend.routers.transactions
  Part 3 - Budget Monitoring          -> backend.routers.budgets
  Part 4 - Dashboard                  -> backend.routers.dashboard

Milestone 2 parts:

  Part 1 - Investment Portfolio Core  -> backend.routers.investments
  Part 2 - Market Data & Returns      -> (extends investments; Alpha Vantage)
  Part 3 - Financial Goal Planning    -> backend.routers.goals
  Part 4 - Portfolio Analytics Dash.  -> backend.routers.portfolio

Run with:
    uvicorn backend.main:app --reload
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import Base, engine

# ---------------------------------------------------------------
# PART 1: Auth models/router - ACTIVE
# ---------------------------------------------------------------
from backend.models import user as user_model            # noqa: F401  (ensures table is registered)
from backend.routers import auth

# ---------------------------------------------------------------
# PART 2: Accounts, Categories & Transactions - ACTIVE
# ---------------------------------------------------------------
from backend.models import account as account_model       # noqa: F401
from backend.models import category as category_model     # noqa: F401
from backend.models import transaction as transaction_model  # noqa: F401
from backend.models import budget as budget_model          # noqa: F401
from backend.routers import accounts, categories, transactions

# ---------------------------------------------------------------
# PART 3: Budget Monitoring - ACTIVE
# ---------------------------------------------------------------
from backend.routers import budgets

# ---------------------------------------------------------------
# PART 4: Financial Dashboard - ACTIVE
# ---------------------------------------------------------------
from backend.routers import dashboard

# ---------------------------------------------------------------
# MILESTONE 2 - PART 1: Investment Portfolio Core - ACTIVE
# ---------------------------------------------------------------
from backend.models import investment as investment_model  # noqa: F401
from backend.routers import investments

# ---------------------------------------------------------------
# MILESTONE 2 - PART 2: Market Data & Returns - ACTIVE
# (extends the investments router; no separate router of its own)
# ---------------------------------------------------------------
from backend.models import price_cache as price_cache_model  # noqa: F401

# ---------------------------------------------------------------
# MILESTONE 2 - PART 3: Financial Goal Planning - ACTIVE
# ---------------------------------------------------------------
from backend.models import goal as goal_model  # noqa: F401
from backend.routers import goals

# ---------------------------------------------------------------
# MILESTONE 2 - SIMULATED TRADING EXTENSION - ACTIVE
# Buy/sell/deposit against an in-app cash wallet; no real money moves.
# ---------------------------------------------------------------
from backend.models import trade as trade_model  # noqa: F401
from backend.routers import trading

# ---------------------------------------------------------------
# MILESTONE 3 - PART: Notifications & Alerts - ACTIVE
# ---------------------------------------------------------------
from backend.models import notification as notification_model  # noqa: F401
from backend.models import user_session as user_session_model  # noqa: F401
from backend.routers import notifications

# ---------------------------------------------------------------
# FINANCIAL HEALTH SCORE MODULE - ACTIVE
# ---------------------------------------------------------------
from backend.models import financial_health as financial_health_model  # noqa: F401

from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from backend.database import SessionLocal
from backend.services.market_data_service import refresh_all_active_symbols

scheduler = BackgroundScheduler()


def _refresh_market_data_job():
    db = SessionLocal()
    try:
        refresh_all_active_symbols(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: same behavior as the old @app.on_event("startup") handler
    scheduler.add_job(_refresh_market_data_job, "interval", minutes=60)
    scheduler.start()
    yield
    # Shutdown: same behavior as the old @app.on_event("shutdown") handler
    scheduler.shutdown()


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Allow the React frontend to call this API. Localhost covers local dev
# (Vite on 5173, CRA on 3000); settings.FRONTEND_URL covers the deployed
# frontend and is skipped if unset/blank so local dev config doesn't break.
_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.FRONTEND_URL:
    _cors_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "FinSight API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


from backend.routers import assistant
from backend.routers import financial_health
from backend.routers import savings
# NOTE: backend/routers/sessions.py is a duplicate, unused implementation of
# session management - the real, working one lives at GET/DELETE
# /auth/sessions inside auth.py (which SessionsCard.jsx on the frontend
# already calls via authApi.js). routers/sessions.py, schemas/session.py,
# and frontend/src/api/sessionsApi.js appear to be an abandoned parallel
# attempt at the same feature and are not imported/used anywhere real.
# Deliberately not registered here to avoid shipping two competing
# /sessions and /auth/sessions endpoints for the same feature.

# ---------------------------------------------------------------
# Router registration (uncomment as each part is built)
# ---------------------------------------------------------------
app.include_router(auth.router)           # Part 1 - ACTIVE
app.include_router(accounts.router)       # Part 2 - ACTIVE
app.include_router(categories.router)     # Part 2 - ACTIVE
app.include_router(transactions.router)   # Part 2 - ACTIVE
app.include_router(budgets.router)        # Part 3 - ACTIVE
app.include_router(dashboard.router)      # Part 4 - ACTIVE
app.include_router(investments.router)    # Milestone 2, Part 1 - ACTIVE
app.include_router(goals.router)          # Milestone 2, Part 3 - ACTIVE
app.include_router(trading.router)        # Milestone 2, Trading extension - ACTIVE
app.include_router(notifications.router)  # Milestone 3, Notifications & Alerts - ACTIVE
app.include_router(assistant.router)      # AI Assistant - ACTIVE
app.include_router(financial_health.router) # Financial Health Score - ACTIVE
app.include_router(savings.router)        # Savings Pool breakdown - ACTIVE