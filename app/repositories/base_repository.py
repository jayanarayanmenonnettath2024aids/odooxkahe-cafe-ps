"""
Base repository with generic CRUD operations.
All domain repositories extend this.
"""

from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async CRUD repository."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(getattr(self.model, "id") == id))
        return result.scalars().first()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[ModelType]:
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        query = select(func.count(getattr(self.model, "id")))
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create(self, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict[str, Any]) -> Optional[ModelType]:
        db_obj = await self.get_by_id(id)
        if db_obj is None:
            return None
        for field, value in obj_in.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get_by_id(id)
        if db_obj is None:
            return False
        await self.db.delete(db_obj)
        await self.db.flush()
        return True
