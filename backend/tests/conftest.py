"""
Shared pytest fixtures.

Tests run against an in-memory SQLite database instead of the real Postgres
instance - fast, no setup required, and disposable per test. This means
these tests exercise the SQLAlchemy models and service-layer logic exactly
as production does, but do NOT catch Postgres-specific behavior (e.g. a
constraint that only Postgres enforces). That trade-off is intentional for
a fast, dependency-free test suite; anything genuinely Postgres-specific
should be called out in that test's docstring.
"""
import os
import sys
from datetime import date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Make `backend.*` importable when running pytest from the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.database import Base
# Import every model so SQLAlchemy can resolve all relationships declared on
# User (investments, goals, trades, notifications, sessions, etc.) - without
# this, mapper configuration fails as soon as any relationship references a
# model class that was never imported anywhere in the test process.
#
# NOTE: backend/models/session.py ALSO defines a class named UserSession
# mapped to the same "user_sessions" table. It is dead code - nothing in
# routers/ or services/ imports it (session_service.py imports UserSession
# from user_session.py instead) - so it is deliberately NOT imported here.
# Importing both in the same process is a SQLAlchemy registry conflict
# (two classes mapped to one table), which is itself evidence this
# duplicate should be deleted from the codebase.
from backend.models.user import User
from backend.models.account import Account
from backend.models.category import Category
from backend.models.transaction import Transaction
from backend.models.budget import Budget
from backend.models.goal import Goal
from backend.models.investment import Investment
from backend.models.trade import Trade
from backend.models.notification import Notification
from backend.models.user_session import UserSession
from backend.models.price_cache import PriceCache
from backend.models.financial_health import FinancialHealthCache


@pytest.fixture()
def db_session():
    """
    A fresh in-memory SQLite database for a single test. StaticPool keeps
    the same in-memory DB alive across the multiple connections a test might
    open (SQLAlchemy would otherwise hand out a brand new empty :memory: db
    per connection).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def make_user(db_session):
    """Factory fixture: create a User row with sane defaults, override via kwargs."""
    def _make_user(**overrides):
        defaults = dict(
            name="Test User",
            email=f"test{id(overrides)}@example.com",
            password_hash="not-a-real-hash",
            currency="INR",
            cash_balance=Decimal("0"),
            savings_pool=Decimal("0"),
            is_verified=True,
            is_active=True,
        )
        defaults.update(overrides)
        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    return _make_user


@pytest.fixture()
def make_account(db_session):
    """Factory fixture: create an Account for a given user."""
    def _make_account(user, **overrides):
        defaults = dict(
            user_id=user.user_id,
            account_name="Cash Amount",
            account_type="wallet",
            balance=Decimal("0"),
            is_active=True,
            is_default=True,
        )
        defaults.update(overrides)
        account = Account(**defaults)
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        return account
    return _make_account


@pytest.fixture()
def make_category(db_session):
    """Factory fixture: create a Category for a given user."""
    def _make_category(user, category_type="expense", **overrides):
        defaults = dict(
            user_id=user.user_id,
            category_name="Groceries" if category_type == "expense" else "Salary",
            category_type=category_type,
        )
        defaults.update(overrides)
        category = Category(**defaults)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category
    return _make_category


@pytest.fixture()
def make_transaction(db_session):
    """Factory fixture: create a Transaction row."""
    def _make_transaction(user, account, category, **overrides):
        defaults = dict(
            user_id=user.user_id,
            account_id=account.account_id,
            category_id=category.category_id if category else None,
            transaction_type="expense",
            amount=Decimal("100.00"),
            transaction_date=date.today(),
        )
        defaults.update(overrides)
        txn = Transaction(**defaults)
        db_session.add(txn)
        db_session.commit()
        db_session.refresh(txn)
        return txn
    return _make_transaction


@pytest.fixture()
def make_goal(db_session):
    """Factory fixture: create a Goal for a given user."""
    def _make_goal(user, **overrides):
        defaults = dict(
            user_id=user.user_id,
            goal_name="Test Goal",
            target_amount=Decimal("10000.00"),
            current_amount=Decimal("0"),
            target_date=date.today() + timedelta(days=365),
        )
        defaults.update(overrides)
        goal = Goal(**defaults)
        db_session.add(goal)
        db_session.commit()
        db_session.refresh(goal)
        return goal
    return _make_goal
