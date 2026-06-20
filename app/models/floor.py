"""
Floor model — restaurant floor plan areas.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    tables = relationship("Table", back_populates="floor", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Floor(id={self.id}, name='{self.name}')>"
