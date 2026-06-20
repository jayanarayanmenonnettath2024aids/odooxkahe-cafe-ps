"""
Customer service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.repo = CustomerRepository(db)

    async def create(self, data: CustomerCreate) -> CustomerResponse:
        customer = await self.repo.create(data.model_dump())
        return CustomerResponse.model_validate(customer)

    async def get_by_id(self, id: int) -> CustomerResponse:
        customer = await self.repo.get_by_id(id)
        if not customer:
            raise NotFoundException("Customer", id)
        return CustomerResponse.model_validate(customer)

    async def get_all(self) -> list[CustomerResponse]:
        customers = await self.repo.get_all()
        return [CustomerResponse.model_validate(c) for c in customers]

    async def update(self, id: int, data: CustomerUpdate) -> CustomerResponse:
        customer = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not customer:
            raise NotFoundException("Customer", id)
        return CustomerResponse.model_validate(customer)

    async def search(self, query: str) -> list[CustomerResponse]:
        customers = await self.repo.search(query)
        return [CustomerResponse.model_validate(c) for c in customers]

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Customer", id)
        return True
