"""
API routes for managing transactions (income/expense/transfer records).
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from backend.schemas.import_transactions import (
    ColumnMapping, ImportPreviewResponse, ImportCommitRequest, ImportCommitResponse,
)
from backend.services.transaction_service import (
    create_transaction,
    get_user_transactions,
    get_transaction_or_404,
    update_transaction,
    delete_transaction,
)
from backend.services.import_service import ImportError_, parse_import_file, commit_import_rows

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record a new income/expense/transfer transaction. Updates the linked account's balance."""
    try:
        return create_transaction(db, current_user.user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List transactions for the current user, most recent first.
    Optional filters: account_id, category_id, transaction_type (income/expense/transfer).
    """
    return get_user_transactions(
        db,
        current_user.user_id,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        limit=limit,
        offset=offset,
    )


# NOTE: both import routes must be declared before "/{transaction_id}" -
# otherwise FastAPI would try to parse "import" as a transaction_id and
# 422 on every call.
@router.post("/import/preview", response_model=ImportPreviewResponse)
async def preview_import(
    account_id: int = Form(...),
    mapping: str = Form(..., description="JSON-encoded ColumnMapping"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Parses an uploaded CSV/Excel bank statement using the given column
    mapping and returns a preview - nothing is saved to the database yet.
    The user reviews/edits the returned rows in the frontend, then calls
    /import/commit with their confirmed selections.
    """
    try:
        mapping_obj = ColumnMapping.model_validate_json(mapping)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid column mapping: {e}")

    file_bytes = await file.read()
    try:
        parsed_rows = parse_import_file(
            db, current_user.user_id, account_id, file_bytes, file.filename, mapping_obj
        )
    except ImportError_ as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return ImportPreviewResponse(
        account_id=account_id,
        total_rows=len(parsed_rows),
        parsed_rows=parsed_rows,
        rows_with_errors=sum(1 for r in parsed_rows if r.parse_error),
        likely_duplicates=sum(1 for r in parsed_rows if r.is_likely_duplicate),
    )


@router.post("/import/commit", response_model=ImportCommitResponse)
def commit_import(
    data: ImportCommitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates real transactions from the rows the user confirmed in the
    preview step (with any edits they made). Each row goes through the same
    create_transaction path as a manually-entered transaction, so account
    balance sync and the overspend/savings-shortfall check both apply.
    """
    created_ids = commit_import_rows(db, current_user.user_id, data.account_id, data.rows)
    return ImportCommitResponse(created_count=len(created_ids), transaction_ids=created_ids)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_transaction_or_404(db, current_user.user_id, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionResponse)
def edit_transaction(
    transaction_id: int,
    updates: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a transaction. Automatically re-syncs the linked account's balance."""
    try:
        return update_transaction(db, current_user.user_id, transaction_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a transaction. Automatically reverses its effect on the account balance."""
    try:
        delete_transaction(db, current_user.user_id, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
