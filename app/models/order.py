"""
Order and OrderItem models — the core transactional entities.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SENT_TO_KITCHEN = "SENT_TO_KITCHEN"
    PREPARING = "PREPARING"
    READY = "READY"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class KitchenStatus(str, enum.Enum):
    TO_COOK = "TO_COOK"
    PREPARING = "PREPARING"
    COMPLETED = "COMPLETED"


class OrderType(str, enum.Enum):
    DINE_IN = "DINE_IN"
    TAKEAWAY = "TAKEAWAY"
    PARCEL = "PARCEL"
    SELF_ORDER = "SELF_ORDER"


# Valid order state transitions
ORDER_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.DRAFT: [OrderStatus.SENT_TO_KITCHEN, OrderStatus.CANCELLED],
    OrderStatus.SENT_TO_KITCHEN: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.READY: [OrderStatus.PAID, OrderStatus.CANCELLED],
    OrderStatus.PAID: [],
    OrderStatus.CANCELLED: [],
}


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("pos_sessions.id"), nullable=False, index=True)
    table_id: Mapped[int | None] = mapped_column(ForeignKey("tables.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # New Takeaway / Parcel fields
    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType), default=OrderType.DINE_IN, index=True)
    pickup_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.DRAFT, index=True
    )
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    coupon_id: Mapped[int | None] = mapped_column(
        ForeignKey("coupons.id", ondelete="SET NULL"), nullable=True
    )
    promotion_id: Mapped[int | None] = mapped_column(
        ForeignKey("promotions.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    session = relationship("PosSession", back_populates="orders", lazy="selectin")
    table = relationship("Table", back_populates="orders", lazy="selectin")
    customer = relationship("Customer", back_populates="orders", lazy="selectin")
    employee = relationship("User", back_populates="orders", lazy="selectin")
    items = relationship(
        "OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, number='{self.order_number}', status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    kitchen_status: Mapped[KitchenStatus] = mapped_column(
        Enum(KitchenStatus), default=KitchenStatus.TO_COOK
    )

    # Relationships
    order = relationship("Order", back_populates="items", lazy="selectin")
    product = relationship("Product", back_populates="order_items", lazy="selectin")

    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, qty={self.quantity})>"
