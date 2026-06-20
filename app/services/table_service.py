"""
Table service — CRUD, QR token management, occupancy tracking.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.table import Table, TableStatus
from app.repositories.table_repository import TableRepository
from app.schemas.table import TableCreate, TableResponse, TableUpdate


class TableService:
    def __init__(self, db: AsyncSession):
        self.repo = TableRepository(db)

    async def create(self, data: TableCreate) -> TableResponse:
        table_data = data.model_dump()
        table_data["unique_token"] = str(uuid.uuid4())
        table = await self.repo.create(table_data)
        return self._to_response(table)

    async def get_by_id(self, id: int) -> TableResponse:
        table = await self.repo.get_by_id(id)
        if not table:
            raise NotFoundException("Table", id)
        return self._to_response(table)

    async def get_all(self) -> list[TableResponse]:
        tables = await self.repo.get_all_with_status()
        return [self._to_response(t) for t in tables]

    async def get_by_floor(self, floor_id: int) -> list[TableResponse]:
        tables = await self.repo.get_by_floor(floor_id)
        return [self._to_response(t) for t in tables]

    async def get_by_token(self, token: str) -> TableResponse:
        table = await self.repo.get_by_token(token)
        if not table:
            raise NotFoundException("Table", f"token={token}")
        return self._to_response(table)

    async def update(self, id: int, data: TableUpdate) -> TableResponse:
        table = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not table:
            raise NotFoundException("Table", id)
        return self._to_response(table)

    async def update_status(self, table_id: int, status: TableStatus) -> TableResponse:
        table = await self.repo.update_status(table_id, status)
        if not table:
            raise NotFoundException("Table", table_id)
        return self._to_response(table)

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Table", id)
        return True

    async def get_status_summary(self) -> list[TableResponse]:
        tables = await self.repo.get_all_with_status()
        return [self._to_response(t) for t in tables]

    def _to_response(self, table: Table) -> TableResponse:
        return TableResponse(
            id=table.id,
            floor_id=table.floor_id,
            floor_name=table.floor.name if table.floor else None,
            table_number=table.table_number,
            seat_count=table.seat_count,
            active_status=table.active_status,
            unique_token=table.unique_token,
        )
