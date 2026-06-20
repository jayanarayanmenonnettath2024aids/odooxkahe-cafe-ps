"""
Promotion model — product/order-level promotional discounts.
"""

import enum

from sqlalchemy import Boolean, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PromotionScope(str, enum.Enum):
    PRODUCT = "PRODUCT"
    ORDER = "ORDER"


class PromotionDiscountType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    promotion_scope: Mapped[PromotionScope] = mapped_column(Enum(PromotionScope), nullable=False)
    minimum_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minimum_order_amount: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    discount_type: Mapped[PromotionDiscountType] = mapped_column(
        Enum(PromotionDiscountType), nullable=False
    )
    discount_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Promotion(id={self.id}, name='{self.name}', scope={self.promotion_scope})>"
