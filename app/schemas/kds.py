"""
KDS (Kitchen Display System) schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.order import KitchenStatus, OrderStatus


class KDSOrderItemResponse(BaseModel):
    id: int
    product_name: str
    quantity: int
    kitchen_status: KitchenStatus

    model_config = {"from_attributes": True}


class KDSOrderResponse(BaseModel):
    id: int
    order_number: str
    order_type: Optional[str] = None
    table_id: Optional[int] = None
    table_number: Optional[str] = None
    floor_name: Optional[str] = None
    status: OrderStatus
    items: list[KDSOrderItemResponse] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class KDSStageUpdateRequest(BaseModel):
    """Move entire order to next kitchen stage."""
    pass  # No body needed, derived from current state


class KDSItemCompleteRequest(BaseModel):
    """Mark a single order item as completed in kitchen."""
    pass  # No body needed
