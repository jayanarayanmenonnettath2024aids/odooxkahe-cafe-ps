"""
Public Coupons router — allows customers to view active promotions/coupons.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.coupon import CouponResponse
from app.services.coupon_service import CouponService

router = APIRouter(prefix="/public/coupons", tags=["Public Offers"])

@router.get("/active", response_model=SuccessResponse[List[CouponResponse]])
async def get_active_coupons(db: AsyncSession = Depends(get_db)):
    """Get all active public coupons for display on the landing page or self-order menu."""
    service = CouponService(db)
    coupons = await service.get_all()
    # Filter only active coupons
    active_coupons = [c for c in coupons if c.is_active]
    return SuccessResponse(data=active_coupons)
