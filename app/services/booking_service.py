"""
Service for Booking management.
"""

from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking, BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingService:
    def __init__(self, db: AsyncSession):
        self.repo = BookingRepository(db)

    async def get_all_bookings(self) -> Sequence[Booking]:
        return await self.repo.get_all()

    async def create_booking(self, data: BookingCreate) -> Booking:
        booking = Booking(
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            booking_time=data.booking_time,
            guest_count=data.guest_count,
            table_id=data.table_id,
            status=BookingStatus.PENDING
        )
        self.repo.add(booking)
        return booking

    async def update_booking(self, booking_id: int, data: BookingUpdate) -> Booking:
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if data.customer_name is not None:
            booking.customer_name = data.customer_name
        if data.customer_phone is not None:
            booking.customer_phone = data.customer_phone
        if data.booking_time is not None:
            booking.booking_time = data.booking_time
        if data.guest_count is not None:
            booking.guest_count = data.guest_count
        if data.table_id is not None:
            booking.table_id = data.table_id
        if data.status is not None:
            booking.status = data.status

        return booking

    async def delete_booking(self, booking_id: int) -> None:
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        await self.repo.delete(booking)
