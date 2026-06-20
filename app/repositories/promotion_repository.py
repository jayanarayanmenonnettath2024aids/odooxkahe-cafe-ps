"""
Promotion repository.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotion import Promotion, PromotionScope
from app.repositories.base_repository import BaseRepository


class PromotionRepository(BaseRepository[Promotion]):
    def __init__(self, db: AsyncSession):
        super().__init__(Promotion, db)

    async def get_active_promotions(
        self, scope: PromotionScope | None = None
    ) -> Sequence[Promotion]:
        query = select(Promotion).where(Promotion.is_active == True)
        if scope:
            query = query.where(Promotion.promotion_scope == scope)
        result = await self.db.execute(query)
        return result.scalars().all()
