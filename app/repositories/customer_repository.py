"""
Customer repository.
"""

from typing import Optional, Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def search(self, query: str) -> Sequence[Customer]:
        result = await self.db.execute(
            select(Customer).where(
                or_(
                    Customer.name.ilike(f"%{query}%"),
                    Customer.email.ilike(f"%{query}%"),
                    Customer.phone.ilike(f"%{query}%"),
                )
            )
        )
        return result.scalars().all()

    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.phone == phone))
        return result.scalars().first()
