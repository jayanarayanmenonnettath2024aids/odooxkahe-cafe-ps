"""
Repository for Booking model.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking


class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[Booking]:
        result = await self.db.execute(select(Booking).order_by(Booking.booking_time))
        return result.scalars().all()

    async def get_by_id(self, booking_id: int) -> Booking | None:
        return await self.db.get(Booking, booking_id)

    def add(self, booking: Booking) -> None:
        self.db.add(booking)

    async def delete(self, booking: Booking) -> None:
        await self.db.delete(booking)
