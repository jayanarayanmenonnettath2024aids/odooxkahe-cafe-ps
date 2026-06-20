"""
Promotion service — promotion engine and CRUD.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.promotion import Promotion, PromotionDiscountType, PromotionScope
from app.repositories.promotion_repository import PromotionRepository
from app.schemas.promotion import PromotionCreate, PromotionResponse, PromotionUpdate


class PromotionService:
    def __init__(self, db: AsyncSession):
        self.repo = PromotionRepository(db)

    async def create(self, data: PromotionCreate) -> PromotionResponse:
        promo = await self.repo.create(data.model_dump())
        return PromotionResponse.model_validate(promo)

    async def get_by_id(self, id: int) -> PromotionResponse:
        promo = await self.repo.get_by_id(id)
        if not promo:
            raise NotFoundException("Promotion", id)
        return PromotionResponse.model_validate(promo)

    async def get_all(self) -> list[PromotionResponse]:
        promos = await self.repo.get_all()
        return [PromotionResponse.model_validate(p) for p in promos]

    async def get_active(self, scope: PromotionScope | None = None) -> list[PromotionResponse]:
        promos = await self.repo.get_active_promotions(scope)
        return [PromotionResponse.model_validate(p) for p in promos]

    async def update(self, id: int, data: PromotionUpdate) -> PromotionResponse:
        promo = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not promo:
            raise NotFoundException("Promotion", id)
        return PromotionResponse.model_validate(promo)

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Promotion", id)
        return True

    @staticmethod
    def calculate_promotion_discount(
        promotion: Promotion,
        order_total: float,
        total_quantity: int,
    ) -> float:
        """
        Promotion engine: check eligibility and calculate discount.
        """
        # Check minimum order amount
        if promotion.promotion_scope == PromotionScope.ORDER:
            if promotion.minimum_order_amount and order_total < float(promotion.minimum_order_amount):
                return 0.0

        # Check minimum quantity
        if promotion.promotion_scope == PromotionScope.PRODUCT:
            if promotion.minimum_quantity and total_quantity < promotion.minimum_quantity:
                return 0.0

        # Calculate discount
        if promotion.discount_type == PromotionDiscountType.PERCENTAGE:
            return round(order_total * float(promotion.discount_value) / 100, 2)
        elif promotion.discount_type == PromotionDiscountType.FIXED:
            return min(float(promotion.discount_value), order_total)

        return 0.0
