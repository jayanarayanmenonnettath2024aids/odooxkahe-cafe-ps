"""
Self-ordering schemas — for customer-facing tablet/QR ordering.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class SelfOrderCartItem(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class SelfOrderPlaceRequest(BaseModel):
    table_token: str
    items: list[SelfOrderCartItem]
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    coupon_code: Optional[str] = None


class SelfOrderStatusResponse(BaseModel):
    order_id: int
    order_number: str
    status: OrderStatus
    items: list[dict] = []
    total_amount: float = 0.0
