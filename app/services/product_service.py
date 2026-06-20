"""
Product service.
"""

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)

    async def create(self, data: ProductCreate) -> ProductResponse:
        product = await self.repo.create(data.model_dump())
        product = await self.repo.get_by_id_with_category(product.id)
        return self._to_response(product)

    async def get_by_id(self, product_id: int) -> ProductResponse:
        product = await self.repo.get_by_id_with_category(product_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return self._to_response(product)

    async def get_all(
        self,
        category_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProductResponse]:
        products = await self.repo.get_active_products(category_id, skip, limit)
        return [self._to_response(p) for p in products]

    async def update(self, product_id: int, data: ProductUpdate) -> ProductResponse:
        update_data = data.model_dump(exclude_unset=True)
        product = await self.repo.update(product_id, update_data)
        if not product:
            raise NotFoundException("Product", product_id)
        product = await self.repo.get_by_id_with_category(product.id)
        return self._to_response(product)

    async def delete(self, product_id: int) -> bool:
        if not await self.repo.delete(product_id):
            raise NotFoundException("Product", product_id)
        return True

    async def search(self, query: str, category_id: int | None = None) -> list[ProductResponse]:
        products = await self.repo.search(query, category_id)
        return [self._to_response(p) for p in products]

    def _to_response(self, product: Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=float(product.price),
            tax_percentage=float(product.tax_percentage),
            unit_of_measure=product.unit_of_measure,
            category_id=product.category_id,
            category_name=product.category.name if product.category else None,
            is_active=product.is_active,
        )
