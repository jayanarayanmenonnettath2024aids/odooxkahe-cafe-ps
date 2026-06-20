"""
Product schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    tax_percentage: float = Field(default=0.0, ge=0, le=100)
    unit_of_measure: Optional[str] = "unit"
    category_id: Optional[int] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    tax_percentage: Optional[float] = Field(None, ge=0, le=100)
    unit_of_measure: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax_percentage: float
    unit_of_measure: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}
