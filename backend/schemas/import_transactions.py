"""
Pydantic schemas for CSV/Excel bank statement import.

Design: a two-step flow, never a single "upload and trust it" call.
  1. /transactions/import/preview - parses the file using the user-provided
     column mapping, returns a list of ParsedImportRow the user reviews and
     edits in the browser (nothing is saved to the DB yet).
  2. /transactions/import/commit - takes the (possibly edited) rows the user
     confirmed and actually creates them as real transactions.

This two-step shape exists specifically so a misparsed file, wrong column
mapping, or bad category guess never silently corrupts the ledger - the user
always sees exactly what will be created before it happens.
"""

from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ColumnMapping(BaseModel):
    """
    Tells the parser which column in the uploaded file maps to which
    transaction field. Column names as they appear in the file's header row.

    Two supported shapes for amount, since banks differ:
      - single 'amount' column with a sign or a separate 'type' indicator, OR
      - separate 'debit_column' and 'credit_column' (common in Indian bank
        statements: "Withdrawal Amt" / "Deposit Amt")
    Exactly one of (amount_column) or (debit_column + credit_column) must be
    provided - enforced in the service, not here, since the failure needs to
    reference the actual file's headers for a useful error message.
    """
    date_column: str
    description_column: str
    amount_column: Optional[str] = None
    debit_column: Optional[str] = None
    credit_column: Optional[str] = None
    date_format: Optional[str] = Field(
        default=None,
        description="e.g. '%d/%m/%Y' - if omitted, common formats are tried automatically",
    )


class ParsedImportRow(BaseModel):
    row_number: int  # 1-indexed position in the original file, for user reference
    transaction_date: Optional[date] = None
    description: str
    amount: Optional[float] = None
    transaction_type: Optional[Literal["income", "expense"]] = None
    suggested_category_id: Optional[int] = None
    suggested_category_name: Optional[str] = None
    is_likely_duplicate: bool = False
    duplicate_of_transaction_id: Optional[int] = None
    parse_error: Optional[str] = None  # e.g. "Could not parse date 'N/A'" - row still shown, but excluded from commit by default


class ImportPreviewResponse(BaseModel):
    account_id: int
    total_rows: int
    parsed_rows: list[ParsedImportRow]
    rows_with_errors: int
    likely_duplicates: int


class ImportRowCommit(BaseModel):
    """One row the user confirmed, with any edits they made in the preview UI."""
    transaction_date: date
    description: str
    amount: float = Field(gt=0)
    transaction_type: Literal["income", "expense"]
    category_id: Optional[int] = None
    payment_mode: Optional[str] = None


class ImportCommitRequest(BaseModel):
    account_id: int
    rows: list[ImportRowCommit] = Field(min_length=1)


class ImportCommitResponse(BaseModel):
    created_count: int
    transaction_ids: list[int]
