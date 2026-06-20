from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> RefreshToken:
        token = RefreshToken(**data)
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalars().first()

    async def revoke_token(self, token: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(revoked=True)
        )
        await self.db.flush()

    async def revoke_all_for_user(self, user_id: int) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
        await self.db.flush()
