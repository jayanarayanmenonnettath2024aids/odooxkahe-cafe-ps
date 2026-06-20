"""
Payment repository.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def get_by_order(self, order_id: int) -> Sequence[Payment]:
        result = await self.db.execute(
            select(Payment)
            .options(selectinload(Payment.payment_method))
            .where(Payment.order_id == order_id)
        )
        return result.scalars().all()

    async def get_by_transaction_reference(self, transaction_reference: str) -> Payment | None:
        result = await self.db.execute(
            select(Payment).where(Payment.transaction_reference == transaction_reference)
        )
        return result.scalars().first()
