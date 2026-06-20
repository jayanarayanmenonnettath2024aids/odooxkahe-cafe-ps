"""
Categories router — CRUD.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import SuccessResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=SuccessResponse[list[CategoryResponse]])
async def list_categories(db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    categories = await service.get_all()
    return SuccessResponse(data=categories)


@router.get("/{category_id}", response_model=SuccessResponse[CategoryResponse])
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    service = CategoryService(db)
    return SuccessResponse(data=await service.get_by_id(category_id))


@router.post("", response_model=SuccessResponse[CategoryResponse])
async def create_category(
    data: CategoryCreate,
    admin = Depends(AdminUser),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    return SuccessResponse(data=await service.create(data), message="Category created")


@router.put("/{category_id}", response_model=SuccessResponse[CategoryResponse])
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    admin = Depends(AdminUser),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    return SuccessResponse(data=await service.update(category_id, data), message="Category updated")


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(
    category_id: int,
    admin = Depends(AdminUser),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    await service.delete(category_id)
    return SuccessResponse(message="Category deleted")
