"""
Tests for backend/services/budget_service.py - specifically
_calculate_spent_amount, the core aggregation that budget tracking and
overspend alerts both depend on.
"""
import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services import budget_service


class TestCalculateSpentAmount:
    def test_sums_only_expense_transactions_not_income(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        today = date.today()
        user = make_user()
        account = make_account(user)
        expense_cat = make_category(user, category_type="expense")
        income_cat = make_category(user, category_type="income")

        make_transaction(
            user, account, expense_cat,
            transaction_type="expense", amount=Decimal("150.00"), transaction_date=today,
        )
        make_transaction(
            user, account, income_cat,
            transaction_type="income", amount=Decimal("5000.00"), transaction_date=today,
        )

        spent = budget_service._calculate_spent_amount(
            db_session, user.user_id, category_id=None, month=today
        )

        assert spent == Decimal("150.00")

    def test_scoped_to_category_when_category_id_given(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        today = date.today()
        user = make_user()
        account = make_account(user)
        food_cat = make_category(user, category_type="expense", category_name="Food")
        transport_cat = make_category(user, category_type="expense", category_name="Transport")

        make_transaction(
            user, account, food_cat,
            transaction_type="expense", amount=Decimal("80.00"), transaction_date=today,
        )
        make_transaction(
            user, account, transport_cat,
            transaction_type="expense", amount=Decimal("40.00"), transaction_date=today,
        )

        food_spent = budget_service._calculate_spent_amount(
            db_session, user.user_id, category_id=food_cat.category_id, month=today
        )

        assert food_spent == Decimal("80.00")

    def test_sums_all_categories_when_category_id_is_none(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        today = date.today()
        user = make_user()
        account = make_account(user)
        food_cat = make_category(user, category_type="expense", category_name="Food")
        transport_cat = make_category(user, category_type="expense", category_name="Transport")

        make_transaction(
            user, account, food_cat,
            transaction_type="expense", amount=Decimal("80.00"), transaction_date=today,
        )
        make_transaction(
            user, account, transport_cat,
            transaction_type="expense", amount=Decimal("40.00"), transaction_date=today,
        )

        total_spent = budget_service._calculate_spent_amount(
            db_session, user.user_id, category_id=None, month=today
        )

        assert total_spent == Decimal("120.00")

    def test_excludes_transactions_outside_the_month(
        self, db_session, make_user, make_account, make_category, make_transaction
    ):
        today = date.today()
        last_month = date(today.year - 1, 12, 15) if today.month == 1 \
            else today.replace(month=today.month - 1, day=15)

        user = make_user()
        account = make_account(user)
        expense_cat = make_category(user, category_type="expense")

        make_transaction(
            user, account, expense_cat,
            transaction_type="expense", amount=Decimal("999.00"), transaction_date=last_month,
        )

        spent_this_month = budget_service._calculate_spent_amount(
            db_session, user.user_id, category_id=None, month=today
        )

        assert spent_this_month == Decimal("0")

    def test_returns_zero_when_no_transactions_exist(self, db_session, make_user):
        today = date.today()
        user = make_user()

        spent = budget_service._calculate_spent_amount(
            db_session, user.user_id, category_id=None, month=today
        )

        assert spent == Decimal("0")
