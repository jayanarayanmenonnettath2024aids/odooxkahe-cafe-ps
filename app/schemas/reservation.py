"""
Reservation schemas.
"""

from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.reservation import ReservationSource, ReservationStatus


class ReservationBase(BaseModel):
    customer_name: str
    customer_email: Optional[EmailStr] = None
    customer_phone: str
    table_id: Optional[int] = None
    reservation_date: date
    start_time: time
    end_time: time
    guest_count: int
    source: ReservationSource = ReservationSource.WEB
    coupon_id: Optional[int] = None
    notes: Optional[str] = None


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    table_id: Optional[int] = None
    notes: Optional[str] = None


class ReservationResponse(ReservationBase):
    id: int
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TableRecommendationRequest(BaseModel):
    reservation_date: date
    start_time: time
    end_time: time
    guest_count: int
