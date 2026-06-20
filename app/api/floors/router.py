"""
Floors router — CRUD.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser
from app.schemas.common import SuccessResponse
from app.schemas.floor import FloorCreate, FloorResponse, FloorUpdate
from app.services.floor_service import FloorService

router = APIRouter(prefix="/floors", tags=["Floors"])


@router.get("", response_model=SuccessResponse[list[FloorResponse]])
async def list_floors(db: AsyncSession = Depends(get_db)):
    service = FloorService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/{floor_id}", response_model=SuccessResponse[FloorResponse])
async def get_floor(floor_id: int, db: AsyncSession = Depends(get_db)):
    service = FloorService(db)
    return SuccessResponse(data=await service.get_by_id(floor_id))


@router.post("", response_model=SuccessResponse[FloorResponse])
async def create_floor(data: FloorCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = FloorService(db)
    return SuccessResponse(data=await service.create(data), message="Floor created")


@router.put("/{floor_id}", response_model=SuccessResponse[FloorResponse])
async def update_floor(floor_id: int, data: FloorUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = FloorService(db)
    return SuccessResponse(data=await service.update(floor_id, data), message="Floor updated")


@router.delete("/{floor_id}", response_model=SuccessResponse)
async def delete_floor(floor_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = FloorService(db)
    await service.delete(floor_id)
    return SuccessResponse(message="Floor deleted")
