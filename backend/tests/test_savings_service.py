"""
Tests for backend/services/savings_service.py.

These specifically lock in two real bugs that were found and fixed in this
service, so they can never silently regress:

  1. ensure_monthly_refill must credit the PREVIOUS month's net savings, not
     the current (barely-started) month's - crediting the current month
     always credits ~0.
  2. The "already refilled this month" check must be an exact match (==) on
     last_savings_refill_month, not >=, so a stamped month that's ahead of
     the real current month (e.g. from a bad manual edit) can self-heal
     instead of permanently blocking all future refills.
"""
import os
import sys
from datetime import date
from decimal import Decimal

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services import savings_service


def _first_of_month(d: date) -> date:
    return d.replace(day=1)


def _previous_month(d: date) -> date:
    first = _first_of_month(d)
    if first.month == 1:
        return date(first.year - 1, 12, 1)
    return first.replace(month=first.month - 1)


class TestEnsureMonthlyRefill:
    def test_refill_credits_previous_month_savings_not_current_month(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        """
        The bug this guards against: an earlier version summed the CURRENT
        month's transactions (which, right after the month starts, is ~0)
        instead of the previous month's. This test puts real income in the
        previous month and none in the current month, and asserts the
        refill amount comes from the previous month.
        """
        today = date.today()
        prev_month_date = _previous_month(today).replace(day=15)

        user = make_user(cash_balance=Decimal("0"), savings_pool=Decimal("0"))
        account = make_account(user)
        income_cat = make_category(user, category_type="income")

        # 5000 income in the PREVIOUS month, nothing in the current month
        make_transaction(
            user, account, income_cat,
            transaction_type="income", amount=Decimal("5000.00"),
            transaction_date=prev_month_date,
        )

        updated_user = savings_service.ensure_monthly_refill(db_session, user.user_id)

        assert updated_user.savings_pool == Decimal("5000.00")
        assert updated_user.last_refill_amount == Decimal("5000.00")
        assert updated_user.last_refill_source_month == _previous_month(today)
        assert updated_user.last_savings_refill_month == _first_of_month(today)

    def test_refill_sweeps_entire_cash_balance_into_pool(
        self, db_session, make_user
    ):
        user = make_user(cash_balance=Decimal("250.00"), savings_pool=Decimal("100.00"))

        updated_user = savings_service.ensure_monthly_refill(db_session, user.user_id)

        # No transactions this test, so the only contribution is the swept wallet cash
        assert updated_user.savings_pool == Decimal("350.00")
        assert updated_user.cash_balance == Decimal("0")

    def test_negative_previous_month_contributes_nothing_not_a_debit(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        """A month where expenses exceeded income must floor at 0, never
        shrink the pool."""
        today = date.today()
        prev_month_date = _previous_month(today).replace(day=15)

        user = make_user(cash_balance=Decimal("0"), savings_pool=Decimal("1000.00"))
        account = make_account(user)
        expense_cat = make_category(user, category_type="expense")

        make_transaction(
            user, account, expense_cat,
            transaction_type="expense", amount=Decimal("500.00"),
            transaction_date=prev_month_date,
        )

        updated_user = savings_service.ensure_monthly_refill(db_session, user.user_id)

        # Pool should stay exactly where it was - not go negative or drop
        assert updated_user.savings_pool == Decimal("1000.00")
        assert updated_user.last_refill_amount == Decimal("0")

    def test_refill_is_idempotent_within_the_same_month(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        """Calling ensure_monthly_refill twice in the same month must not
        double-credit the pool."""
        today = date.today()
        prev_month_date = _previous_month(today).replace(day=15)

        user = make_user(cash_balance=Decimal("0"), savings_pool=Decimal("0"))
        account = make_account(user)
        income_cat = make_category(user, category_type="income")
        make_transaction(
            user, account, income_cat,
            transaction_type="income", amount=Decimal("2000.00"),
            transaction_date=prev_month_date,
        )

        first = savings_service.ensure_monthly_refill(db_session, user.user_id)
        second = savings_service.ensure_monthly_refill(db_session, user.user_id)

        assert first.savings_pool == Decimal("2000.00")
        assert second.savings_pool == Decimal("2000.00")  # unchanged, not doubled

    def test_stamped_month_ahead_of_real_month_self_heals(
        self, db_session, make_user
    ):
        """
        Regression test for the >= vs == bug: if last_savings_refill_month
        is somehow ahead of the real current month (bad manual edit, clock
        issue), the refill must still run - not treat "ahead" as "already
        done forever".
        """
        today = date.today()
        future_month = date(today.year + 1, 1, 1)

        user = make_user(cash_balance=Decimal("500.00"), savings_pool=Decimal("0"))
        user.last_savings_refill_month = future_month
        db_session.commit()

        updated_user = savings_service.ensure_monthly_refill(db_session, user.user_id)

        # The wallet cash should have been swept - proving the refill ran
        # rather than being skipped because "future_month >= current_month".
        assert updated_user.cash_balance == Decimal("0")
        assert updated_user.savings_pool == Decimal("500.00")
        assert updated_user.last_savings_refill_month == _first_of_month(today)

    def test_raises_for_nonexistent_user(self, db_session):
        with pytest.raises(ValueError):
            savings_service.ensure_monthly_refill(db_session, user_id=999999)


class TestGetSavingsPool:
    def test_display_total_includes_this_month_running_contribution(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        """
        Regression test for the display-vs-ledger bug: the dashboard total
        must include this month's not-yet-swept savings on top of the
        stored ledger balance, so the number the user sees isn't stale
        until next month's refill.
        """
        today = date.today()
        user = make_user(cash_balance=Decimal("0"), savings_pool=Decimal("1000.00"))
        account = make_account(user)
        income_cat = make_category(user, category_type="income")

        # Income booked THIS month - should show up in the display total
        # even though it hasn't been swept into savings_pool yet.
        make_transaction(
            user, account, income_cat,
            transaction_type="income", amount=Decimal("300.00"),
            transaction_date=today,
        )

        display_total = savings_service.get_savings_pool(db_session, user.user_id)

        assert display_total == Decimal("1300.00")

    def test_display_total_does_not_double_count_after_refill_runs(
        self, db_session, make_user
    ):
        # No transactions at all - display total should just equal the
        # stored ledger balance with 0 running contribution.
        user = make_user(cash_balance=Decimal("0"), savings_pool=Decimal("750.00"))

        display_total = savings_service.get_savings_pool(db_session, user.user_id)

        assert display_total == Decimal("750.00")


class TestGetSavingsBreakdown:
    def test_breakdown_total_matches_pool_plus_this_month_contribution(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        """
        Regression test: the breakdown popup's top-line total must equal
        the sum of its own component rows (previously it showed the raw
        stored balance while the rows below summed to a different total).

        Note: get_savings_breakdown calls ensure_monthly_refill first, which
        sweeps the full cash_balance into savings_pool immediately - so the
        starting cash_balance ends up counted inside "savings_pool", not
        separately, by the time the breakdown is built.
        """
        today = date.today()
        user = make_user(cash_balance=Decimal("0"), savings_pool=Decimal("500.00"))
        account = make_account(user)
        income_cat = make_category(user, category_type="income")
        make_transaction(
            user, account, income_cat,
            transaction_type="income", amount=Decimal("200.00"),
            transaction_date=today,
        )

        breakdown = savings_service.get_savings_breakdown(db_session, user.user_id)

        assert breakdown["savings_pool"] == 700.0  # 500 stored + 200 this month
        assert breakdown["this_month_contribution"] == 200.0
        assert breakdown["wallet_cash_pending_sweep"] == 0.0

    def test_breakdown_includes_goal_allocations(
        self, db_session, make_user, make_goal
    ):
        user = make_user(savings_pool=Decimal("1000.00"))
        make_goal(user, goal_name="Emergency Fund", current_amount=Decimal("300.00"))
        make_goal(user, goal_name="Vacation", current_amount=Decimal("150.00"))

        breakdown = savings_service.get_savings_breakdown(db_session, user.user_id)

        assert breakdown["total_allocated_to_goals"] == 450.0
        assert len(breakdown["goal_allocations"]) == 2

    def test_breakdown_labels_source_month_as_one_before_trigger_month(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        """
        Regression test: last_refill_month (shown as "Added from <month>")
        must be the month whose savings were actually credited - not the
        month the refill happened to trigger in.
        """
        today = date.today()
        prev_month_date = _previous_month(today).replace(day=10)

        user = make_user(savings_pool=Decimal("0"))
        account = make_account(user)
        income_cat = make_category(user, category_type="income")
        make_transaction(
            user, account, income_cat,
            transaction_type="income", amount=Decimal("100.00"),
            transaction_date=prev_month_date,
        )

        breakdown = savings_service.get_savings_breakdown(db_session, user.user_id)

        assert breakdown["last_refill_month"] == _previous_month(today).isoformat()
        assert breakdown["last_refill_triggered_month"] == _first_of_month(today).isoformat()
