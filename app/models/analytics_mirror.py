"""
Analytics mirror models — decoupled tables for data warehouse and reporting sync.
"""

from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OrdersAnalytics(Base):
    __tablename__ = "orders_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_order_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PaymentsAnalytics(Base):
    __tablename__ = "payments_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_payment_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ReservationsAnalytics(Base):
    __tablename__ = "reservations_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_reservation_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class CustomerAnalytics(Base):
    __tablename__ = "customer_analytics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_customer_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
