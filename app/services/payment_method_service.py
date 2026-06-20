"""
Payment method service.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.repositories.payment_method_repository import PaymentMethodRepository
from app.schemas.payment_method import (
    PaymentMethodCreate,
    PaymentMethodResponse,
    PaymentMethodUpdate,
)


class PaymentMethodService:
    def __init__(self, db: AsyncSession):
        self.repo = PaymentMethodRepository(db)

    async def create(self, data: PaymentMethodCreate) -> PaymentMethodResponse:
        pm = await self.repo.create(data.model_dump())
        return PaymentMethodResponse.model_validate(pm)

    async def get_by_id(self, id: int) -> PaymentMethodResponse:
        pm = await self.repo.get_by_id(id)
        if not pm:
            raise NotFoundException("PaymentMethod", id)
        return PaymentMethodResponse.model_validate(pm)

    async def get_all(self) -> list[PaymentMethodResponse]:
        pms = await self.repo.get_all()
        return [PaymentMethodResponse.model_validate(pm) for pm in pms]

    async def get_enabled(self) -> list[PaymentMethodResponse]:
        pms = await self.repo.get_enabled()
        return [PaymentMethodResponse.model_validate(pm) for pm in pms]

    async def update(self, id: int, data: PaymentMethodUpdate) -> PaymentMethodResponse:
        pm = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not pm:
            raise NotFoundException("PaymentMethod", id)
        return PaymentMethodResponse.model_validate(pm)

    async def toggle_enabled(self, id: int, enabled: bool) -> PaymentMethodResponse:
        pm = await self.repo.update(id, {"enabled": enabled})
        if not pm:
            raise NotFoundException("PaymentMethod", id)
        return PaymentMethodResponse.model_validate(pm)

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("PaymentMethod", id)
        return True

    def generate_upi_payload(self, upi_id: str, amount: float, name: str = "CafePOS") -> str:
        """Generate UPI deep link payload."""
        return (
            f"upi://pay?pa={upi_id}"
            f"&pn={name}"
            f"&am={amount:.2f}"
            f"&cu=INR"
        )
