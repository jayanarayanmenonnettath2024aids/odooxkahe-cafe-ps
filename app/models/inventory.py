"""
Inventory model — tracks product stock levels for AI insights.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True, index=True)
    current_stock: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    minimum_stock: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    reorder_level: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    unit: Mapped[str] = mapped_column(String(20), default="unit")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, name='{self.name}', current_stock={self.current_stock})>"
