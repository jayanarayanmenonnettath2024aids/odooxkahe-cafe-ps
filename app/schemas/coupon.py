"""
Coupon schemas.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.models.coupon import DiscountType


class CouponCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    expiry_date: Optional[date] = None
    is_active: bool = True


class CouponUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = Field(None, gt=0)
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None


class CouponResponse(BaseModel):
    id: int
    code: str
    discount_type: DiscountType
    discount_value: float
    expiry_date: Optional[date] = None
    is_active: bool

    model_config = {"from_attributes": True}


class CouponValidateRequest(BaseModel):
    code: str
    order_total: Optional[float] = None


class CouponValidateResponse(BaseModel):
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: Optional[float] = None
    message: str = ""
