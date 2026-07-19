"""
Category services - default category seeding + CRUD logic.
"""

from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.schemas.category import CategoryCreate, CategoryUpdate

# Seeded automatically for every new user on registration .
# (icon values are just identifiers - the frontend maps these to actual icons)
DEFAULT_CATEGORIES = [
    {"category_name": "Salary", "category_type": "income", "icon": "briefcase"},
    {"category_name": "Freelance/Other Income", "category_type": "income", "icon": "cash"},
    {"category_name": "Food & Dining", "category_type": "expense", "icon": "utensils"},
    {"category_name": "Transportation", "category_type": "expense", "icon": "car"},
    {"category_name": "Housing", "category_type": "expense", "icon": "home"},
    {"category_name": "Utilities", "category_type": "expense", "icon": "bolt"},
    {"category_name": "Entertainment", "category_type": "expense", "icon": "film"},
    {"category_name": "Shopping", "category_type": "expense", "icon": "bag"},
    {"category_name": "Healthcare", "category_type": "expense", "icon": "heart"},
    {"category_name": "Others", "category_type": "expense", "icon": "dots"},
]

def seed_default_categories(db: Session, user_id: int) -> None:
    """
    Create the default category set for a newly registered user.
    Called once, right after registration succeeds.
    """
    categories = [
        Category(
            user_id=user_id,
            category_name=c["category_name"],
            category_type=c["category_type"],
            icon=c["icon"],
            is_default=True,
        )
        for c in DEFAULT_CATEGORIES
    ]
    db.add_all(categories)
    db.commit()

def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    """Create a custom (non-default) category for the user."""
    existing = (
        db.query(Category)
        .filter(Category.user_id == user_id, Category.category_name == data.category_name)
        .first()
    )
    if existing:
        raise ValueError("A category with this name already exists.")
    
    category = Category(
        user_id=user_id,
        category_name=data.category_name,
        category_type=data.category_type,
        icon=data.icon,
        is_default=False,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_user_categories(db: Session, user_id: int) -> list[Category]:
    return db.query(Category).filter(Category.user_id==user_id).order_by(Category.category_name).all()

def get_category_or_404(db:Session, user_id: int, category_id: int) -> Category:
    category = (
        db.query(Category)
        .filter(Category.category_id==category_id, Category.user_id == user_id)
        .first()
    )
    if not category:
        raise ValueError("Category not found")
    return category

def update_category(db: Session, user_id: int, category_id: int, updates: CategoryUpdate) -> Category:
    category = get_category_or_404(db, user_id, category_id)
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category

def delete_category(db: Session, user_id: int, category_id: int) -> None:
    category = get_category_or_404(db, user_id, category_id)
    if category.is_default:
        raise ValueError("Default categories cannot be deleted")
    db.delete(category)
    db.commit()