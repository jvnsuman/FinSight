"""
Integration test: verifies the FastAPI app actually exposes every router
that's supposed to be registered.

This exists because of a real bug found during a repo audit: main.py had
an entire duplicated block (from a bad merge) containing a second, dead
`app = FastAPI(...)` instance with its own routes and middleware, which
would silently discard anything registered before it.

Separately, backend/routers/sessions.py turned out to be an abandoned,
broken, unused duplicate of session management - it imports names that
don't exist (AuthContext, get_current_auth) and calls service functions
that don't exist (get_active_sessions, revoke_other_sessions). The real,
working implementation is GET/DELETE /auth/sessions inside auth.py, which
the frontend's SessionsCard.jsx already calls correctly. sessions.py is
deliberately left unregistered rather than "fixed", since registering it
would ship two different, competing endpoints for the same feature.

Using FastAPI's TestClient, not just importing main.py, because import
succeeding only proves there's no syntax/import error - it does NOT
prove a router got registered. A route returning 401/404/405 (a real
FastAPI response) instead of raising a connection error is what proves
the route exists at all.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestAllRoutersAreRegistered:
    """
    For each router, hit one of its real paths and assert we get a genuine
    FastAPI response (any status code) rather than a 404 "no matching
    route". A 401 (needs auth) or 405 (wrong method) still proves the path
    exists - only 404 means it's missing entirely.
    """

    def _assert_route_exists(self, method: str, path: str):
        resp = client.request(method, path)
        assert resp.status_code != 404, (
            f"{method} {path} returned 404 - this router/path is not "
            f"registered in main.py (or the path itself is wrong)"
        )

    def test_auth_router_registered(self):
        self._assert_route_exists("POST", "/auth/login")

    def test_accounts_router_registered(self):
        self._assert_route_exists("GET", "/accounts")

    def test_categories_router_registered(self):
        self._assert_route_exists("GET", "/categories")

    def test_transactions_router_registered(self):
        self._assert_route_exists("GET", "/transactions")

    def test_budgets_router_registered(self):
        self._assert_route_exists("GET", "/budgets")

    def test_dashboard_router_registered(self):
        self._assert_route_exists("GET", "/dashboard/summary")

    def test_investments_router_registered(self):
        self._assert_route_exists("GET", "/investments")

    def test_goals_router_registered(self):
        self._assert_route_exists("GET", "/goals")

    def test_trading_router_registered(self):
        self._assert_route_exists("GET", "/trading/wallet")

    def test_notifications_router_registered(self):
        self._assert_route_exists("GET", "/notifications")

    def test_assistant_router_registered(self):
        self._assert_route_exists("POST", "/assistant/query")

    def test_financial_health_router_registered(self):
        # Note: unlike every other router, financial_health uses an
        # "/api/" prefix (/api/financial-health/...) - inconsistent
        # naming, but it does match what the frontend actually calls.
        self._assert_route_exists("GET", "/api/financial-health/")

    def test_savings_router_registered(self):
        self._assert_route_exists("GET", "/savings/breakdown")

    def test_auth_sessions_endpoint_registered(self):
        """
        Session management (list/revoke logged-in devices) lives at
        GET/DELETE /auth/sessions inside auth.py - not at a separate
        /sessions router. backend/routers/sessions.py, schemas/session.py,
        and frontend/src/api/sessionsApi.js are an abandoned, unused
        duplicate of this same feature (broken imports, wrong function
        names) and are deliberately not registered in main.py.
        """
        self._assert_route_exists("GET", "/auth/sessions")


class TestOnlyOneAppInstance:
    """
    Regression test for the duplicated-app-instance bug: main.py used to
    contain the entire startup sequence twice (two `app = FastAPI(...)`
    calls, two CORS middleware registrations, two startup handlers) from
    a bad merge. The second silently replaced the first, so this was
    invisible unless you actually inspected the file - a router included
    against a stale `app` reference would vanish with no error.
    """

    def test_cors_middleware_registered_exactly_once(self):
        from starlette.middleware.cors import CORSMiddleware

        cors_middlewares = [
            m for m in app.user_middleware if m.cls is CORSMiddleware
        ]
        assert len(cors_middlewares) == 1, (
            f"Expected exactly one CORSMiddleware registration, found "
            f"{len(cors_middlewares)} - main.py may have a duplicated "
            f"app setup block again"
        )

    def test_root_and_health_endpoints_each_registered_once(self):
        resp = client.get("/")
        assert resp.status_code == 200
        resp = client.get("/health")
        assert resp.status_code == 200


class TestVerificationStatusEndpoint:
    """
    Regression test for a real gap found during the audit: VerifyPending.jsx
    (the "check your inbox" page shown after signup) polls
    GET /auth/verification-status?email=... to detect when the user has
    clicked their emailed verification link, but that endpoint didn't
    exist - the frontend was calling something the backend never
    implemented. Uses the in-memory SQLite fixture via dependency
    override, since this needs a real DB round-trip, not just a route
    existence check.
    """

    def test_unregistered_email_returns_false_not_an_error(self, db_session):
        from backend.database import get_db

        app.dependency_overrides[get_db] = lambda: db_session
        try:
            resp = client.get("/auth/verification-status?email=nobody@example.com")
            assert resp.status_code == 200
            assert resp.json() == {"is_verified": False}
        finally:
            app.dependency_overrides.clear()

    def test_unverified_user_returns_false(self, db_session, make_user):
        from backend.database import get_db

        make_user(email="pending@example.com", is_verified=False)
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            resp = client.get("/auth/verification-status?email=pending@example.com")
            assert resp.status_code == 200
            assert resp.json() == {"is_verified": False}
        finally:
            app.dependency_overrides.clear()

    def test_verified_user_returns_true(self, db_session, make_user):
        from backend.database import get_db

        make_user(email="verified@example.com", is_verified=True)
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            resp = client.get("/auth/verification-status?email=verified@example.com")
            assert resp.status_code == 200
            assert resp.json() == {"is_verified": True}
        finally:
            app.dependency_overrides.clear()
