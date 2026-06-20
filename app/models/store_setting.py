"""
Store Setting model — for mobile order and general store settings.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StoreSetting(Base):
    __tablename__ = "store_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    store_name: Mapped[str] = mapped_column(String(100), default="Odoo Cafe")
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    online_ordering_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    pay_at_counter_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    splash_background_color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    splash_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<StoreSetting(store_name='{self.store_name}')>"
