"""
Customer model — cafe customers.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    # Relationships
    orders = relationship("Order", back_populates="customer", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name='{self.name}')>"
