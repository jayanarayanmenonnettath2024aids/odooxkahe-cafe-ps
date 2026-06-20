"""
Self-ordering router — QR code-based customer ordering.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.product import ProductResponse
from app.schemas.self_ordering import SelfOrderPlaceRequest, SelfOrderStatusResponse
from app.services.product_service import ProductService
from app.services.self_ordering_service import SelfOrderingService

router = APIRouter(prefix="/s", tags=["Self-Ordering"])


@router.get("/{table_token}")
async def get_table_info(table_token: str, db: AsyncSession = Depends(get_db)):
    """Public endpoint — customer scans QR code."""
    service = SelfOrderingService(db)
    table_info = await service.get_table_by_token(table_token)
    return SuccessResponse(data=table_info)


@router.get("/{table_token}/products", response_model=SuccessResponse[list[ProductResponse]])
async def get_self_order_products(
    table_token: str,
    category_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Browse products for self-ordering."""
    product_service = ProductService(db)
    return SuccessResponse(data=await product_service.get_all(category_id))


@router.post("/{table_token}/order", response_model=SuccessResponse[SelfOrderStatusResponse])
async def place_self_order(
    table_token: str,
    data: SelfOrderPlaceRequest,
    db: AsyncSession = Depends(get_db),
):
    """Place a self-service order."""
    data.table_token = table_token
    service = SelfOrderingService(db)
    result = await service.place_order(data)
    return SuccessResponse(data=result, message="Order placed successfully")


@router.get("/order/{order_id}/status", response_model=SuccessResponse[SelfOrderStatusResponse])
async def track_self_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Track order status."""
    service = SelfOrderingService(db)
    return SuccessResponse(data=await service.track_order(order_id))
