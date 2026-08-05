"""
User ORM model - maps to `users` table.
"""

from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DATE, TIMESTAMP, func
from sqlalchemy.orm import relationship

from backend.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(10), nullable=True)
    profession = Column(String(100), nullable=True)
    monthly_income = Column(DECIMAL(12, 2), nullable=True)
    currency = Column(String(10), default="INR")

    # --- Simulated trading wallet (Milestone 2, Trading extension) ---
    # Not real money - a purely in-app balance the user funds manually and
    # trades against. Starts at 0; never negative (enforced in trade_service).
    cash_balance = Column(DECIMAL(14, 2), nullable=False, default=0)

    # --- Persistent savings pool (Goal-funding extension) ---
    # Separate from cash_balance. This is what goal allocations actually draw
    # down, and what an over-budget expense draws down automatically before
    # ever touching a goal. Refilled once per calendar month (see
    # savings_service.ensure_monthly_refill) with that month's
    # (income - expenses), plus a one-time sweep of any leftover cash_balance
    # at the moment of refill (not continuously - the wallet still needs to
    # hold cash for trades in between refills).
    savings_pool = Column(DECIMAL(14, 2), nullable=False, default=0)
    last_savings_refill_month = Column(DATE, nullable=True)
    # How much the most recent refill actually added to savings_pool - the
    # previous month's (income - expenses), floored at 0, PLUS whatever
    # cash_balance was swept in at that same moment. Recorded purely for
    # display (the "added from last month" line in the savings breakdown
    # popup) - savings_pool itself is still the only real running balance.
    last_refill_amount = Column(DECIMAL(14, 2), nullable=False, default=0)
    # The month whose (income - expenses) last_refill_amount was actually
    # computed from - always the month BEFORE last_savings_refill_month,
    # since a refill triggered in August always credits July's savings, not
    # August's. Stored explicitly (rather than re-deriving "one month
    # before last_savings_refill_month" wherever it's displayed) so the
    # breakdown popup can't drift out of sync with what was actually swept
    # in - that mismatch is exactly what showed "Added from August" for
    # savings that were actually July's.
    last_refill_source_month = Column(DATE, nullable=True)

    # --- Email Verification ---
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True, index=True)
    verification_token_expires = Column(TIMESTAMP, nullable=True)

    # --- Password reset ---
    reset_token = Column(String(255), nullable=True, index=True)
    reset_token_expires = Column(TIMESTAMP, nullable=True)

    # --- Session Invalidation ---
    # Embedded into every JWT as "tv". Bumped on password reset so old tokens
    # (signed with the previous value) are rejected even through they haven't expired.
    token_version = Column(Integer, default=0, nullable=False)

    # --- Account deactivation (soft-delete) ---
    # is_active=False + deletion_requested_at stamped marks the account as
    # deactivated. account_cleanup_service.purge_expired_deleted_accounts
    # permanently removes accounts whose grace period (default 30 days) has
    # passed since deletion_requested_at. A still-null deletion_requested_at
    # with is_active=True means the account is normal/active.
    is_active = Column(Boolean, default=True, nullable=False)
    deletion_requested_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships to other tables 
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")