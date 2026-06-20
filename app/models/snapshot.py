"""
Snapshot models — Immutable historical tracking for audits and year-end reporting.
"""

from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OrderSnapshot(Base):
    __tablename__ = "order_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    snapshot_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PaymentSnapshot(Base):
    __tablename__ = "payment_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_payment_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    snapshot_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ReservationSnapshot(Base):
    __tablename__ = "reservation_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_reservation_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    snapshot_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class DailySalesSnapshot(Base):
    __tablename__ = "daily_sales_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    snapshot_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    snapshot_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
