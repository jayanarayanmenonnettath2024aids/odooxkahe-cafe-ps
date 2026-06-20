"""
Order and POS terminal schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.order import KitchenStatus, OrderStatus


# --- Order Item Schemas ---

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    tax_amount: float
    discount_amount: float
    line_total: float
    kitchen_status: KitchenStatus

    model_config = {"from_attributes": True}


# --- Order Schemas ---

class OrderResponse(BaseModel):
    id: int
    order_number: str
    session_id: int
    table_id: int
    table_number: Optional[str] = None
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    employee_id: int
    employee_name: Optional[str] = None
    status: OrderStatus
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    items: list[OrderItemResponse] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# --- POS Cart Schemas ---

class CartAddProductRequest(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartUpdateQuantityRequest(BaseModel):
    order_item_id: int
    quantity: int = Field(..., ge=0)  # 0 = remove


class CartRemoveProductRequest(BaseModel):
    order_item_id: int


# --- POS Order Schemas ---

class SelectTableRequest(BaseModel):
    table_id: int
    session_id: int


class AssignCustomerRequest(BaseModel):
    order_id: int
    customer_id: int


class ApplyCouponRequest(BaseModel):
    order_id: int
    coupon_code: str


class ApplyPromotionRequest(BaseModel):
    order_id: int
    promotion_id: int


class SendToKitchenRequest(BaseModel):
    order_id: int


# --- Order Summary ---

class OrderSummaryResponse(BaseModel):
    order_id: int
    order_number: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    item_count: int
    status: OrderStatus


# --- POS Session Schemas ---

class OpenSessionRequest(BaseModel):
    opening_balance: float = Field(default=0.0, ge=0)


class CloseSessionRequest(BaseModel):
    session_id: int
    closing_balance: float = Field(default=0.0, ge=0)


class SessionResponse(BaseModel):
    id: int
    opened_by: int
    opened_by_name: Optional[str] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    opening_balance: float
    closing_balance: Optional[float] = None
    status: str

    model_config = {"from_attributes": True}
