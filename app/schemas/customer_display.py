"""
Customer Display schemas.
"""

from typing import Optional

from pydantic import BaseModel

from app.models.order import OrderStatus


class CustomerDisplayItemResponse(BaseModel):
    product_name: str
    quantity: int
    unit_price: float
    line_total: float


class CustomerDisplayResponse(BaseModel):
    order_id: int
    order_number: str
    items: list[CustomerDisplayItemResponse] = []
    subtotal: float = 0.0
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    total_amount: float = 0.0
    payment_status: OrderStatus = OrderStatus.DRAFT
    table_number: Optional[str] = None
