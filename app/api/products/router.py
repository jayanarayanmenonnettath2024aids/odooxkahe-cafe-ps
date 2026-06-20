"""
Products router — CRUD, search, category filter.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser, EmployeeUser
from app.schemas.common import SuccessResponse
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=SuccessResponse[list[ProductResponse]])
async def list_products(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    if search:
        products = await service.search(search, category_id)
    else:
        products = await service.get_all(category_id, skip, limit)
    return SuccessResponse(data=products)


@router.get("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ProductService(db)
    product = await service.get_by_id(product_id)
    return SuccessResponse(data=product)


@router.post("", response_model=SuccessResponse[ProductResponse])
async def create_product(
    data: ProductCreate,
    admin = Depends(AdminUser),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.create(data)
    return SuccessResponse(data=product, message="Product created")


@router.put("/{product_id}", response_model=SuccessResponse[ProductResponse])
async def update_product(
    product_id: int,
    data: ProductUpdate,
    admin = Depends(AdminUser),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    product = await service.update(product_id, data)
    return SuccessResponse(data=product, message="Product updated")


@router.delete("/{product_id}", response_model=SuccessResponse)
async def delete_product(
    product_id: int,
    admin = Depends(AdminUser),
    db: AsyncSession = Depends(get_db),
):
    service = ProductService(db)
    await service.delete(product_id)
    return SuccessResponse(message="Product deleted")
