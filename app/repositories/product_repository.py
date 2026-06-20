"""
Product repository.
"""

from typing import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_id_with_category(self, id: int):
        result = await self.db.execute(
            select(Product).options(selectinload(Product.category)).where(Product.id == id)
        )
        return result.scalars().first()

    async def get_active_products(
        self,
        category_id: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Product]:
        query = select(Product).options(selectinload(Product.category)).where(
            Product.is_active == True
        )
        if category_id:
            query = query.where(Product.category_id == category_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search(self, query: str, category_id: int | None = None) -> Sequence[Product]:
        stmt = (
            select(Product)
            .options(selectinload(Product.category))
            .where(
                Product.is_active == True,
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                ),
            )
        )
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
