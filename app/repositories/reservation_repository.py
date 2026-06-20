"""
Reservation repository.
"""

from datetime import date, time

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.reservation import Reservation, ReservationStatus


class ReservationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> Reservation:
        reservation = Reservation(**data)
        self.db.add(reservation)
        await self.db.flush()
        return reservation

    async def get_by_id(self, id: int) -> Reservation | None:
        result = await self.db.execute(
            select(Reservation)
            .options(selectinload(Reservation.table), selectinload(Reservation.coupon))
            .where(Reservation.id == id)
        )
        return result.scalars().first()

    async def get_all(self, for_date: date | None = None) -> list[Reservation]:
        query = select(Reservation).options(selectinload(Reservation.table))
        if for_date:
            query = query.where(Reservation.reservation_date == for_date)
        result = await self.db.execute(query.order_by(Reservation.start_time))
        return list(result.scalars().all())

    async def check_overlap(
        self,
        table_id: int,
        res_date: date,
        start_t: time,
        end_t: time,
        exclude_id: int | None = None,
    ) -> bool:
        """Check if a table is already reserved during the given time slot."""
        query = select(Reservation).where(
            Reservation.table_id == table_id,
            Reservation.reservation_date == res_date,
            Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.CONFIRMED, ReservationStatus.SEATED]),
            or_(
                and_(Reservation.start_time <= start_t, Reservation.end_time > start_t),
                and_(Reservation.start_time < end_t, Reservation.end_time >= end_t),
                and_(Reservation.start_time >= start_t, Reservation.end_time <= end_t),
            )
        )
        if exclude_id:
            query = query.where(Reservation.id != exclude_id)
            
        result = await self.db.execute(query)
        overlapping = result.scalars().first()
        return overlapping is not None

    async def update(self, id: int, data: dict) -> Reservation | None:
        reservation = await self.get_by_id(id)
        if not reservation:
            return None
        for key, value in data.items():
            setattr(reservation, key, value)
        await self.db.flush()
        return reservation

    async def delete(self, id: int) -> bool:
        reservation = await self.get_by_id(id)
        if not reservation:
            return False
        await self.db.delete(reservation)
        await self.db.flush()
        return True
