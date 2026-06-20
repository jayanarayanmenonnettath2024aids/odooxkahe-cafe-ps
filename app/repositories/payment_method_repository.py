"""
Payment method repository.
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_method import PaymentMethod
from app.repositories.base_repository import BaseRepository


class PaymentMethodRepository(BaseRepository[PaymentMethod]):
    def __init__(self, db: AsyncSession):
        super().__init__(PaymentMethod, db)

    async def get_by_name(self, name: str) -> Optional[PaymentMethod]:
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.name == name)
        )
        return result.scalars().first()

    async def get_enabled(self) -> Sequence[PaymentMethod]:
        result = await self.db.execute(
            select(PaymentMethod).where(PaymentMethod.enabled == True)
        )
        return result.scalars().all()
