"""
Floor service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.floor_repository import FloorRepository
from app.schemas.floor import FloorCreate, FloorResponse, FloorUpdate


class FloorService:
    def __init__(self, db: AsyncSession):
        self.repo = FloorRepository(db)

    async def create(self, data: FloorCreate) -> FloorResponse:
        floor = await self.repo.create(data.model_dump())
        return FloorResponse(id=floor.id, name=floor.name, table_count=0)

    async def get_by_id(self, id: int) -> FloorResponse:
        floor = await self.repo.get_with_tables(id)
        if not floor:
            raise NotFoundException("Floor", id)
        return FloorResponse(
            id=floor.id,
            name=floor.name,
            table_count=len(floor.tables) if floor.tables else 0,
        )

    async def get_all(self) -> list[FloorResponse]:
        floors = await self.repo.get_all_with_tables()
        return [
            FloorResponse(
                id=f.id,
                name=f.name,
                table_count=len(f.tables) if f.tables else 0,
            )
            for f in floors
        ]

    async def update(self, id: int, data: FloorUpdate) -> FloorResponse:
        floor = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not floor:
            raise NotFoundException("Floor", id)
        return FloorResponse(id=floor.id, name=floor.name)

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Floor", id)
        return True
