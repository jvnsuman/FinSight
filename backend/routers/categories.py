""""
API routes for managing categories (defaults are seeded  on registration).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from backend.services.category_service import (
    create_category,
    get_user_categories,
    update_category,
    delete_category,
)

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def add_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a custom category (defaults already exist from registration)."""
    try:
        return create_category(db, current_user.user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all categories (defaults + custom) for the current user."""
    return get_user_categories(db, current_user.user_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def edit_category(
    category_id: int,
    updates: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_category(db, current_user.user_id, category_id, updates)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a custom category. Default categories cannot be deleted."""
    try:
        delete_category(db, current_user.user_id, category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
