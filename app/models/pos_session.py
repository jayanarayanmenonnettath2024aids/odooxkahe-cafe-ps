"""
POS Session model — tracks opening/closing of point-of-sale sessions.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SessionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PosSession(Base):
    __tablename__ = "pos_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    opened_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opening_balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    closing_balance: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus), default=SessionStatus.OPEN
    )

    # Relationships
    opened_by_user = relationship("User", back_populates="pos_sessions", lazy="selectin")
    orders = relationship("Order", back_populates="session", lazy="selectin")

    def __repr__(self) -> str:
        return f"<PosSession(id={self.id}, status={self.status})>"
