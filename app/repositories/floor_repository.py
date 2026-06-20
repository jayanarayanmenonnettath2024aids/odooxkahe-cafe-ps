"""
Floor repository.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.floor import Floor
from app.repositories.base_repository import BaseRepository


class FloorRepository(BaseRepository[Floor]):
    def __init__(self, db: AsyncSession):
        super().__init__(Floor, db)

    async def get_with_tables(self, floor_id: int):
        result = await self.db.execute(
            select(Floor).options(selectinload(Floor.tables)).where(Floor.id == floor_id)
        )
        return result.scalars().first()

    async def get_all_with_tables(self):
        result = await self.db.execute(
            select(Floor).options(selectinload(Floor.tables)).order_by(Floor.name)
        )
        return result.scalars().all()
