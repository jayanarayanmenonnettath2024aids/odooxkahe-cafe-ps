"""
Router for Bookings.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from app.schemas.common import SuccessResponse
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("", response_model=SuccessResponse[List[BookingResponse]])
async def list_bookings(user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = BookingService(db)
    bookings = await service.get_all_bookings()
    return SuccessResponse(data=bookings)


@router.post("", response_model=SuccessResponse[BookingResponse])
async def create_booking(data: BookingCreate, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = BookingService(db)
    booking = await service.create_booking(data)
    return SuccessResponse(data=booking, message="Booking created successfully")


@router.put("/{booking_id}", response_model=SuccessResponse[BookingResponse])
async def update_booking(booking_id: int, data: BookingUpdate, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = BookingService(db)
    booking = await service.update_booking(booking_id, data)
    return SuccessResponse(data=booking, message="Booking updated successfully")


@router.delete("/{booking_id}", response_model=SuccessResponse)
async def delete_booking(booking_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = BookingService(db)
    await service.delete_booking(booking_id)
    return SuccessResponse(message="Booking deleted successfully")
