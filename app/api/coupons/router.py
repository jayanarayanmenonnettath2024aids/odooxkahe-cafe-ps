"""
Coupons router — CRUD + validate.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser, EmployeeUser
from app.schemas.common import SuccessResponse
from app.schemas.coupon import CouponCreate, CouponResponse, CouponUpdate, CouponValidateRequest, CouponValidateResponse
from app.services.coupon_service import CouponService

router = APIRouter(prefix="/coupons", tags=["Coupons"])


@router.get("", response_model=SuccessResponse[list[CouponResponse]])
async def list_coupons(admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = CouponService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/{coupon_id}", response_model=SuccessResponse[CouponResponse])
async def get_coupon(coupon_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = CouponService(db)
    return SuccessResponse(data=await service.get_by_id(coupon_id))


@router.post("", response_model=SuccessResponse[CouponResponse])
async def create_coupon(data: CouponCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = CouponService(db)
    return SuccessResponse(data=await service.create(data), message="Coupon created")


@router.put("/{coupon_id}", response_model=SuccessResponse[CouponResponse])
async def update_coupon(coupon_id: int, data: CouponUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = CouponService(db)
    return SuccessResponse(data=await service.update(coupon_id, data), message="Coupon updated")


@router.delete("/{coupon_id}", response_model=SuccessResponse)
async def delete_coupon(coupon_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = CouponService(db)
    await service.delete(coupon_id)
    return SuccessResponse(message="Coupon deleted")


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(data: CouponValidateRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = CouponService(db)
    return await service.validate(data)
