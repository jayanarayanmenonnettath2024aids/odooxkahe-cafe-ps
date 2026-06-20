"""
Tables router — CRUD + by-floor + status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser
from app.schemas.common import SuccessResponse
from app.schemas.table import TableCreate, TableResponse, TableUpdate
from app.services.table_service import TableService

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("", response_model=SuccessResponse[list[TableResponse]])
async def list_tables(db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/status", response_model=SuccessResponse[list[TableResponse]])
async def get_table_status(db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_status_summary())


@router.get("/by-floor/{floor_id}", response_model=SuccessResponse[list[TableResponse]])
async def get_tables_by_floor(floor_id: int, db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_by_floor(floor_id))


@router.get("/{table_id}", response_model=SuccessResponse[TableResponse])
async def get_table(table_id: int, db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_by_id(table_id))


@router.post("", response_model=SuccessResponse[TableResponse])
async def create_table(data: TableCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.create(data), message="Table created")


@router.put("/{table_id}", response_model=SuccessResponse[TableResponse])
async def update_table(table_id: int, data: TableUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.update(table_id, data), message="Table updated")


@router.delete("/{table_id}", response_model=SuccessResponse)
async def delete_table(table_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    await service.delete(table_id)
    return SuccessResponse(message="Table deleted")
