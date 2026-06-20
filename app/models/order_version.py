"""
OrderVersion model — Historical tracking for order lifecycle.
"""

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderVersion(Base):
    __tablename__ = "order_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)
    old_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    order = relationship("Order", lazy="selectin")
    user = relationship("User", lazy="selectin")

    def __repr__(self) -> str:
        return f"<OrderVersion(order_id={self.order_id}, version={self.version}, type='{self.change_type}')>"
