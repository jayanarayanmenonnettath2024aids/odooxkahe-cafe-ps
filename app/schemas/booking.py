"""
Schemas for Booking.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    customer_name: str = Field(..., max_length=100)
    customer_phone: str = Field(..., max_length=20)
    booking_time: datetime
    guest_count: int = Field(..., gt=0)
    table_id: Optional[int] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, max_length=100)
    customer_phone: Optional[str] = Field(None, max_length=20)
    booking_time: Optional[datetime] = None
    guest_count: Optional[int] = Field(None, gt=0)
    table_id: Optional[int] = None
    status: Optional[BookingStatus] = None


class BookingResponse(BookingBase):
    id: int
    status: BookingStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
