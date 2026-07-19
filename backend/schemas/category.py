"""
Pydantic schemas for category.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

CATEGORY_TYPES = Literal["income", "expense"]

class CategoryCreate(BaseModel):
    category_name: str = Field(min_length=2, max_length=100)
    category_type: CATEGORY_TYPES
    icon: Optional[str] = Field(default=None, max_length=50)

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    icon: Optional[str] = None

class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    category_type: str
    icon: Optional[str] = None
    is_default: bool

    model_config = ConfigDict(from_attributes=True)