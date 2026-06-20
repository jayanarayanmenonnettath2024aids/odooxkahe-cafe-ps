"""
Payment model — tracks payment transactions per order.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey("payment_methods.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_reference: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    # Relationships
    order = relationship("Order", back_populates="payments", lazy="selectin")
    payment_method = relationship("PaymentMethod", back_populates="payments", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status})>"
