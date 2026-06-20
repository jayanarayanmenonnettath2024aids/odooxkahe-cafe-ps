"""
Promotion schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.promotion import PromotionDiscountType, PromotionScope


class PromotionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    promotion_scope: PromotionScope
    minimum_quantity: Optional[int] = Field(None, ge=1)
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    discount_type: PromotionDiscountType
    discount_value: float = Field(..., gt=0)
    is_active: bool = True


class PromotionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    promotion_scope: Optional[PromotionScope] = None
    minimum_quantity: Optional[int] = Field(None, ge=1)
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    discount_type: Optional[PromotionDiscountType] = None
    discount_value: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class PromotionResponse(BaseModel):
    id: int
    name: str
    promotion_scope: PromotionScope
    minimum_quantity: Optional[int] = None
    minimum_order_amount: Optional[float] = None
    discount_type: PromotionDiscountType
    discount_value: float
    is_active: bool

    model_config = {"from_attributes": True}
