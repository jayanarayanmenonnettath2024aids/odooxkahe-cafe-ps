"""
Customer Display router — real-time order view.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.customer_display import CustomerDisplayResponse
from app.services.customer_display_service import CustomerDisplayService
from app.core.dependencies import EmployeeUser
from pydantic import BaseModel

class PushActiveOrderRequest(BaseModel):
    session_id: int
    order_id: int | None = None
    cart_data: dict | None = None

router = APIRouter(prefix="/customer-display", tags=["Customer Display"])


@router.get("/{order_id}", response_model=SuccessResponse[CustomerDisplayResponse])
async def get_customer_display(order_id: int, db: AsyncSession = Depends(get_db)):
    """Public endpoint — no auth required for customer-facing display."""
    service = CustomerDisplayService(db)
    return SuccessResponse(data=await service.get_display(order_id))


@router.post("/push-active-order", response_model=SuccessResponse)
async def push_active_order(
    data: PushActiveOrderRequest,
    user=Depends(EmployeeUser)
):
    """Cashier terminal pushes the active order to the customer display."""
    from app.core.websocket_manager import ws_manager
    await ws_manager.broadcast_to_channel(
        f"customer_display:session:{data.session_id}",
        "active_order_changed",
        {"order_id": data.order_id, "cart_data": data.cart_data}
    )
    return SuccessResponse(message="Pushed active order to customer display")
