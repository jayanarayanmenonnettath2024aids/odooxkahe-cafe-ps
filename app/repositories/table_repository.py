"""
Table repository.
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.table import Table, TableStatus
from app.repositories.base_repository import BaseRepository


class TableRepository(BaseRepository[Table]):
    def __init__(self, db: AsyncSession):
        super().__init__(Table, db)

    async def get_by_floor(self, floor_id: int) -> Sequence[Table]:
        result = await self.db.execute(
            select(Table)
            .options(selectinload(Table.floor))
            .where(Table.floor_id == floor_id)
            .order_by(Table.table_number)
        )
        return result.scalars().all()

    async def get_by_token(self, token: str) -> Optional[Table]:
        result = await self.db.execute(
            select(Table)
            .options(selectinload(Table.floor))
            .where(Table.unique_token == token)
        )
        return result.scalars().first()

    async def get_all_with_status(self) -> Sequence[Table]:
        result = await self.db.execute(
            select(Table)
            .options(selectinload(Table.floor))
            .order_by(Table.floor_id, Table.table_number)
        )
        return result.scalars().all()

    async def update_status(self, table_id: int, status: TableStatus) -> Optional[Table]:
        table = await self.get_by_id(table_id)
        if table:
            table.active_status = status
            await self.db.flush()
            await self.db.refresh(table)
        return table
