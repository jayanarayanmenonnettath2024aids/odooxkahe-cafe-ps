"""
Table model — individual tables on floors with QR token support.
"""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TableStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"


class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)
    table_number: Mapped[str] = mapped_column(String(20), nullable=False)
    seat_count: Mapped[int] = mapped_column(Integer, default=4)
    active_status: Mapped[TableStatus] = mapped_column(
        Enum(TableStatus), default=TableStatus.AVAILABLE
    )
    unique_token: Mapped[str] = mapped_column(
        String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True
    )

    # Relationships
    floor = relationship("Floor", back_populates="tables", lazy="selectin")
    orders = relationship("Order", back_populates="table", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Table(id={self.id}, number='{self.table_number}', status={self.active_status})>"
