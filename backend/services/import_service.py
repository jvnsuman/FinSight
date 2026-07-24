"""
Transaction import service - parses an uploaded CSV/Excel bank statement into
ParsedImportRow objects for user review, and commits confirmed rows as real
transactions.

Deliberately NOT trying to auto-detect every bank's column layout. The user
tells us (via ColumnMapping) which column is which - this is safer than
guessing, since a wrong guess in a finance app means wrong money, and no
guessing heuristic covers every bank's export format anyway.

Category matching is a simple case-insensitive substring match against the
user's existing category names within the transaction description - not a
real classifier. It's meant to save re-typing the obvious cases (a
description containing "salary" suggesting an existing "Salary" category),
not to be authoritative; the user confirms or changes it in the preview step
regardless.
"""

import io
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.models.transaction import Transaction
from backend.schemas.import_transactions import ColumnMapping, ParsedImportRow
from backend.services.transaction_service import create_transaction
from backend.schemas.transaction import TransactionCreate


class ImportError_(Exception):
    """Raised for file-level problems (bad file, missing mapped column, etc.)."""


# Common date formats tried in order when no explicit date_format is given.
# Day-first formats are listed first since this targets Indian bank exports.
_CANDIDATE_DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
    "%Y-%m-%d", "%m/%d/%Y", "%d %b %Y", "%d %B %Y",
]


def _read_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    lower = filename.lower()
    try:
        if lower.endswith(".csv"):
            return pd.read_csv(io.BytesIO(file_bytes), dtype=str, keep_default_na=False)
        elif lower.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(file_bytes), dtype=str)
        else:
            raise ImportError_("Unsupported file type - please upload a .csv or .xlsx file.")
    except ImportError_:
        raise
    except Exception as e:
        raise ImportError_(f"Could not read this file: {e}")


def _parse_date(raw: str, explicit_format: Optional[str]) -> Optional[date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    formats_to_try = [explicit_format] if explicit_format else _CANDIDATE_DATE_FORMATS
    for fmt in formats_to_try:
        if not fmt:
            continue
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_amount(raw: str) -> Optional[Decimal]:
    if raw is None:
        return None
    cleaned = str(raw).strip().replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "")
    if not cleaned:
        return None
    # pandas stringifies an empty/NaN Excel cell as the literal text "nan"
    # when read with dtype=str. Decimal("nan") does NOT raise - it silently
    # succeeds as a NaN value, which then breaks downstream comparisons
    # (Decimal("nan") < 0 raises InvalidOperation) or produces wrong results.
    # Must be caught explicitly here, before it ever reaches Decimal().
    if cleaned.lower() in ("nan", "none", "null", "na", "n/a", "-"):
        return None
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1]
    try:
        value = Decimal(cleaned)
        if not value.is_finite():  # guards any other NaN/Infinity spelling that slips through
            return None
        return -value if negative else value
    except InvalidOperation:
        return None


def _suggest_category(db: Session, user_id: int, description: str, transaction_type: str) -> Optional[Category]:
    if not description:
        return None
    categories = (
        db.query(Category)
        .filter(Category.user_id == user_id, Category.category_type == transaction_type)
        .all()
    )
    description_lower = description.lower()
    for cat in categories:
        if cat.category_name.lower() in description_lower:
            return cat
    return None


def _check_duplicate(db: Session, user_id: int, account_id: int, txn_date: date, amount: Decimal, description: str) -> Optional[int]:
    """
    Flags a row as a likely duplicate if an existing transaction on the same
    account has the same date, the same amount, and a similar description
    (case-insensitive exact match on description - deliberately strict rather
    than fuzzy, since a false "not a duplicate" is far less costly here than
    a false "is a duplicate" that causes a real transaction to be silently
    skipped).
    """
    existing = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.account_id == account_id,
            Transaction.transaction_date == txn_date,
            Transaction.amount == amount,
        )
        .all()
    )
    for t in existing:
        if (t.description or "").strip().lower() == (description or "").strip().lower():
            return t.transaction_id
    return None


def parse_import_file(
    db: Session, user_id: int, account_id: int, file_bytes: bytes, filename: str, mapping: ColumnMapping
) -> list[ParsedImportRow]:
    if not mapping.amount_column and not (mapping.debit_column and mapping.credit_column):
        raise ImportError_(
            "Provide either 'amount_column', or both 'debit_column' and 'credit_column'."
        )

    df = _read_file(file_bytes, filename)

    required_columns = [mapping.date_column, mapping.description_column]
    if mapping.amount_column:
        required_columns.append(mapping.amount_column)
    else:
        required_columns.extend([mapping.debit_column, mapping.credit_column])

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ImportError_(
            f"These mapped columns don't exist in the file: {', '.join(missing)}. "
            f"Columns found in the file: {', '.join(df.columns)}"
        )

    rows: list[ParsedImportRow] = []
    for idx, raw_row in df.iterrows():
        row_number = idx + 2  # +1 for 0-index, +1 for header row
        description = str(raw_row[mapping.description_column]).strip()
        parsed_date = _parse_date(str(raw_row[mapping.date_column]), mapping.date_format)

        amount: Optional[Decimal] = None
        transaction_type: Optional[str] = None
        parse_error = None

        if mapping.amount_column:
            amount_raw = _parse_amount(str(raw_row[mapping.amount_column]))
            if amount_raw is not None:
                transaction_type = "expense" if amount_raw < 0 else "income"
                amount = abs(amount_raw)
        else:
            debit = _parse_amount(str(raw_row[mapping.debit_column]))
            credit = _parse_amount(str(raw_row[mapping.credit_column]))
            if debit and debit != 0:
                amount, transaction_type = abs(debit), "expense"
            elif credit and credit != 0:
                amount, transaction_type = abs(credit), "income"

        if parsed_date is None:
            parse_error = f"Could not parse date '{raw_row[mapping.date_column]}'"
        elif amount is None:
            parse_error = "Could not determine an amount for this row"

        suggested_category = None
        if not parse_error:
            suggested_category = _suggest_category(db, user_id, description, transaction_type)

        is_duplicate = False
        duplicate_id = None
        if not parse_error:
            duplicate_id = _check_duplicate(db, user_id, account_id, parsed_date, amount, description)
            is_duplicate = duplicate_id is not None

        rows.append(ParsedImportRow(
            row_number=row_number,
            transaction_date=parsed_date,
            description=description,
            amount=float(amount) if amount is not None else None,
            transaction_type=transaction_type,
            suggested_category_id=suggested_category.category_id if suggested_category else None,
            suggested_category_name=suggested_category.category_name if suggested_category else None,
            is_likely_duplicate=is_duplicate,
            duplicate_of_transaction_id=duplicate_id,
            parse_error=parse_error,
        ))

    return rows


def commit_import_rows(db: Session, user_id: int, account_id: int, rows: list) -> list[int]:
    """
    Actually creates transactions from user-confirmed rows. Reuses
    transaction_service.create_transaction for each row so account-balance
    sync and the overspend/savings-shortfall check apply exactly the same as
    a manually-entered transaction - an imported expense that blows the
    budget should warn the user too, not bypass that check silently.
    """
    created_ids = []
    for row in rows:
        txn = create_transaction(db, user_id, TransactionCreate(
            account_id=account_id,
            category_id=row.category_id,
            transaction_type=row.transaction_type,
            amount=row.amount,
            description=row.description,
            payment_mode=row.payment_mode,
            transaction_date=row.transaction_date,
        ))
        created_ids.append(txn.transaction_id)
    return created_ids
