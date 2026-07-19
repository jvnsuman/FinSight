"""add missing user profile columns

Revision ID: a18d06e7e499
Revises: 
Create Date: 2026-07-11 15:49:17.955403

NOTE (fixed during a later debugging pass): this migration originally did
nothing (`pass`), even though it is the root of the entire migration chain.
The base tables (users, accounts, categories, transactions, budgets) were
never actually created by Alembic - they only ever existed because
`Base.metadata.create_all()` was called directly in backend/main.py on
every app startup, silently bootstrapping them outside the migration
history entirely. That call has been removed from main.py (see
CONTRIBUTING.md), which surfaced this gap: running `alembic upgrade head`
against a genuinely empty database failed with "no such table: users"
before this fix. This migration now creates the base schema explicitly, so
the chain is self-sufficient from a truly empty database.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a18d06e7e499'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=10), nullable=True),
        sa.Column('profession', sa.String(length=100), nullable=True),
        sa.Column('monthly_income', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('verification_token_expires', sa.TIMESTAMP(), nullable=True),
        sa.Column('reset_token', sa.String(length=255), nullable=True),
        sa.Column('reset_token_expires', sa.TIMESTAMP(), nullable=True),
        sa.Column('token_version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_verification_token'), 'users', ['verification_token'], unique=False)
    op.create_index(op.f('ix_users_reset_token'), 'users', ['reset_token'], unique=False)

    op.create_table(
        'accounts',
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('account_name', sa.String(length=100), nullable=False),
        sa.Column('account_type', sa.String(length=20), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('balance', sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('account_id'),
    )
    op.create_index(op.f('ix_accounts_account_id'), 'accounts', ['account_id'], unique=False)
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'], unique=False)

    op.create_table(
        'categories',
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_name', sa.String(length=100), nullable=False),
        sa.Column('category_type', sa.String(length=20), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('category_id'),
    )
    op.create_index(op.f('ix_categories_category_id'), 'categories', ['category_id'], unique=False)
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)

    op.create_table(
        'transactions',
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('payment_mode', sa.String(length=255), nullable=True),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.category_id'], ),
        sa.PrimaryKeyConstraint('transaction_id'),
    )
    op.create_index(op.f('ix_transactions_transaction_id'), 'transactions', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_account_id'), 'transactions', ['account_id'], unique=False)
    op.create_index(op.f('ix_transactions_category_id'), 'transactions', ['category_id'], unique=False)

    op.create_table(
        'budgets',
        sa.Column('budget_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.category_id'], ),
        sa.PrimaryKeyConstraint('budget_id'),
    )
    op.create_index(op.f('ix_budgets_category_id'), 'budgets', ['category_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_budgets_category_id'), table_name='budgets')
    op.drop_table('budgets')

    op.drop_index(op.f('ix_transactions_category_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_account_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_transaction_id'), table_name='transactions')
    op.drop_table('transactions')

    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_category_id'), table_name='categories')
    op.drop_table('categories')

    op.drop_index(op.f('ix_accounts_user_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_account_id'), table_name='accounts')
    op.drop_table('accounts')

    op.drop_index(op.f('ix_users_reset_token'), table_name='users')
    op.drop_index(op.f('ix_users_verification_token'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')

