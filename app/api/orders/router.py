"""
Payment methods router — CRUD + enable/disable.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser
from app.schemas.common import SuccessResponse
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodResponse, PaymentMethodUpdate
from app.services.payment_method_service import PaymentMethodService

router = APIRouter(prefix="/payment-methods", tags=["Payment Methods"])


@router.get("", response_model=SuccessResponse[list[PaymentMethodResponse]])
async def list_payment_methods(db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/enabled", response_model=SuccessResponse[list[PaymentMethodResponse]])
async def list_enabled_payment_methods(db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    return SuccessResponse(data=await service.get_enabled())


@router.get("/{pm_id}", response_model=SuccessResponse[PaymentMethodResponse])
async def get_payment_method(pm_id: int, db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    return SuccessResponse(data=await service.get_by_id(pm_id))


@router.post("", response_model=SuccessResponse[PaymentMethodResponse])
async def create_payment_method(data: PaymentMethodCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    return SuccessResponse(data=await service.create(data), message="Payment method created")


@router.put("/{pm_id}", response_model=SuccessResponse[PaymentMethodResponse])
async def update_payment_method(pm_id: int, data: PaymentMethodUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    return SuccessResponse(data=await service.update(pm_id, data), message="Payment method updated")


@router.patch("/{pm_id}/toggle", response_model=SuccessResponse[PaymentMethodResponse])
async def toggle_payment_method(pm_id: int, enabled: bool, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    return SuccessResponse(data=await service.toggle_enabled(pm_id, enabled))


@router.delete("/{pm_id}", response_model=SuccessResponse)
async def delete_payment_method(pm_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PaymentMethodService(db)
    await service.delete(pm_id)
    return SuccessResponse(message="Payment method deleted")
