"""
POS Session repository.
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pos_session import PosSession, SessionStatus
from app.repositories.base_repository import BaseRepository


class SessionRepository(BaseRepository[PosSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(PosSession, db)

    async def get_open_session(self) -> Optional[PosSession]:
        result = await self.db.execute(
            select(PosSession)
            .options(selectinload(PosSession.opened_by_user))
            .where(PosSession.status == SessionStatus.OPEN)
            .order_by(PosSession.opened_at.desc())
        )
        return result.scalars().first()

    async def get_sessions(
        self, status: SessionStatus | None = None, skip: int = 0, limit: int = 50
    ) -> Sequence[PosSession]:
        query = select(PosSession).options(selectinload(PosSession.opened_by_user))
        if status:
            query = query.where(PosSession.status == status)
        query = query.order_by(PosSession.opened_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
