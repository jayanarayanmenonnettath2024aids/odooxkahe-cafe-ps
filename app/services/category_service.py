"""
Category service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    async def create(self, data: CategoryCreate) -> CategoryResponse:
        category = await self.repo.create(data.model_dump())
        return CategoryResponse.model_validate(category)

    async def get_by_id(self, id: int) -> CategoryResponse:
        category = await self.repo.get_by_id(id)
        if not category:
            raise NotFoundException("Category", id)
        return CategoryResponse.model_validate(category)

    async def get_all(self) -> list[CategoryResponse]:
        categories = await self.repo.get_all()
        return [CategoryResponse.model_validate(c) for c in categories]

    async def update(self, id: int, data: CategoryUpdate) -> CategoryResponse:
        category = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not category:
            raise NotFoundException("Category", id)
        return CategoryResponse.model_validate(category)

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Category", id)
        return True
