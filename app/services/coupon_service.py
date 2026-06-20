"""
Coupon service — validation engine and CRUD.
"""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CouponValidationException, NotFoundException
from app.models.coupon import Coupon, DiscountType
from app.repositories.coupon_repository import CouponRepository
from app.schemas.coupon import (
    CouponCreate,
    CouponResponse,
    CouponUpdate,
    CouponValidateRequest,
    CouponValidateResponse,
)


class CouponService:
    def __init__(self, db: AsyncSession):
        self.repo = CouponRepository(db)

    async def create(self, data: CouponCreate) -> CouponResponse:
        coupon = await self.repo.create(data.model_dump())
        return CouponResponse.model_validate(coupon)

    async def get_by_id(self, id: int) -> CouponResponse:
        coupon = await self.repo.get_by_id(id)
        if not coupon:
            raise NotFoundException("Coupon", id)
        return CouponResponse.model_validate(coupon)

    async def get_all(self) -> list[CouponResponse]:
        coupons = await self.repo.get_all()
        return [CouponResponse.model_validate(c) for c in coupons]

    async def update(self, id: int, data: CouponUpdate) -> CouponResponse:
        coupon = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not coupon:
            raise NotFoundException("Coupon", id)
        return CouponResponse.model_validate(coupon)

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Coupon", id)
        return True

    async def validate(self, data: CouponValidateRequest) -> CouponValidateResponse:
        """Validate a coupon code and calculate discount."""
        coupon = await self.repo.get_by_code(data.code)

        if not coupon:
            return CouponValidateResponse(valid=False, message="Coupon not found")

        if not coupon.is_active:
            return CouponValidateResponse(valid=False, message="Coupon is inactive")

        if coupon.expiry_date and coupon.expiry_date < date.today():
            return CouponValidateResponse(valid=False, message="Coupon has expired")

        discount_amount = self.calculate_discount(coupon, data.order_total or 0)

        return CouponValidateResponse(
            valid=True,
            coupon=CouponResponse.model_validate(coupon),
            discount_amount=discount_amount,
            message="Coupon is valid",
        )

    @staticmethod
    def calculate_discount(coupon: Coupon, order_total: float) -> float:
        """Calculate the discount amount from a coupon."""
        if coupon.discount_type == DiscountType.PERCENTAGE:
            return round(order_total * float(coupon.discount_value) / 100, 2)
        elif coupon.discount_type == DiscountType.FIXED:
            return min(float(coupon.discount_value), order_total)
        return 0.0
