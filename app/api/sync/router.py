"""
Sync router — APIs for offline-first capabilities.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.common import SuccessResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["Offline Sync"])


@router.post("/orders")
async def sync_orders(
    data: List[Dict[str, Any]],
    user=Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = SyncService(db)
    result = await service.sync_orders(data)
    return SuccessResponse(data=result, message="Orders synchronized")


@router.post("/cart")
async def sync_cart(
    data: List[Dict[str, Any]],
    user=Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = SyncService(db)
    result = await service.sync_cart(data)
    return SuccessResponse(data=result, message="Cart synchronized")


@router.post("/status")
async def sync_status(
    data: List[Dict[str, Any]],
    user=Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = SyncService(db)
    result = await service.sync_status(data)
    return SuccessResponse(data=result, message="Status synchronized")


@router.get("/pending")
async def get_pending_sync(
    user=Depends(EmployeeUser), db: AsyncSession = Depends(get_db)
):
    service = SyncService(db)
    result = await service.get_pending_sync()
    return SuccessResponse(data=result, message="Pending sync data")
