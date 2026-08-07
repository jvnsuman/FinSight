# Backend Tests

Run from the repo root with:

```bash
pip install -r backend/requirements.txt
pip install pytest
pytest backend/tests -v
```

## What's covered

- `test_security.py` - password hashing, JWT issuing/verification, device-info
  parsing (`backend/core/security.py`). Pure functions, no database.
- `test_savings_service.py` - the monthly savings-pool auto-refill logic
  (`backend/services/savings_service.py`), including regression tests for
  two real bugs found and fixed: crediting the wrong month's savings, and
  an `==` vs `>=` comparison that could permanently block future refills.
- `test_budget_service.py` - spent-amount aggregation
  (`backend/services/budget_service.py`) that budget tracking and overspend
  alerts both depend on.

## How it works

Tests run against an in-memory SQLite database (see `conftest.py`), not the
real Postgres instance - no setup required, and each test gets a fresh,
disposable database. This exercises the actual SQLAlchemy models and
service-layer logic, but doesn't catch anything that's genuinely
Postgres-specific.

## What's not covered yet

This is a starting suite, not full coverage. Not yet tested: routers/API
endpoints (would need a test client + auth fixtures), the import/statement
parsing service, the AI assistant/financial health services (would need
mocking the Gemini API), and the notification/scheduler jobs.
