"""
Kitchen Display System router.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.common import SuccessResponse
from app.schemas.kds import KDSOrderItemResponse, KDSOrderResponse
from app.services.kds_service import KDSService

router = APIRouter(prefix="/kds", tags=["Kitchen Display System"])


@router.get("/orders", response_model=SuccessResponse[list[KDSOrderResponse]])
async def get_kds_orders(user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = KDSService(db)
    return SuccessResponse(data=await service.get_kitchen_orders())


@router.get("/orders/search", response_model=SuccessResponse[list[KDSOrderResponse]])
async def search_kds_orders(
    q: str = Query(...),
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = KDSService(db)
    return SuccessResponse(data=await service.search_orders(q))


@router.patch("/order/{order_id}/next-stage", response_model=SuccessResponse[KDSOrderResponse])
async def advance_order_stage(
    order_id: int,
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = KDSService(db)
    return SuccessResponse(data=await service.advance_order_stage(order_id), message="Order advanced")


@router.patch("/item/{item_id}/complete", response_model=SuccessResponse[KDSOrderItemResponse])
async def complete_item(
    item_id: int,
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = KDSService(db)
    return SuccessResponse(data=await service.complete_item(item_id), message="Item completed")
