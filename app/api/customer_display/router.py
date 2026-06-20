"""
Customer Display router — real-time order view.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.customer_display import CustomerDisplayResponse
from app.services.customer_display_service import CustomerDisplayService

router = APIRouter(prefix="/customer-display", tags=["Customer Display"])


@router.get("/{order_id}", response_model=SuccessResponse[CustomerDisplayResponse])
async def get_customer_display(order_id: int, db: AsyncSession = Depends(get_db)):
    """Public endpoint — no auth required for customer-facing display."""
    service = CustomerDisplayService(db)
    return SuccessResponse(data=await service.get_display(order_id))
