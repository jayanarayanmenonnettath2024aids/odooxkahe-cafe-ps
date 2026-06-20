"""
Payment method model — CASH, CARD, UPI.
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    upi_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    payments = relationship("Payment", back_populates="payment_method", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PaymentMethod(id={self.id}, name='{self.name}', enabled={self.enabled})>"
