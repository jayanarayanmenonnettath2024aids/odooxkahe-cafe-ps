"""
Reservation model — Advanced booking system.
"""

import enum
from datetime import date, datetime, time, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReservationStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SEATED = "SEATED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class ReservationSource(str, enum.Enum):
    WEB = "WEB"
    CALL = "CALL"
    WALK_IN = "WALK_IN"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    table_id: Mapped[int | None] = mapped_column(ForeignKey("tables.id", ondelete="SET NULL"), nullable=True, index=True)
    
    reservation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    guest_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), default=ReservationStatus.PENDING, index=True)
    source: Mapped[ReservationSource] = mapped_column(Enum(ReservationSource), default=ReservationSource.WEB)
    
    coupon_id: Mapped[int | None] = mapped_column(ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    table = relationship("Table", lazy="selectin")
    coupon = relationship("Coupon", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Reservation(id={self.id}, name='{self.customer_name}', status='{self.status}')>"
