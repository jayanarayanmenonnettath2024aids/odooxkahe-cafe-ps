"""
Promotions router — CRUD.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser
from app.schemas.common import SuccessResponse
from app.schemas.promotion import PromotionCreate, PromotionResponse, PromotionUpdate
from app.services.promotion_service import PromotionService

router = APIRouter(prefix="/promotions", tags=["Promotions"])


@router.get("", response_model=SuccessResponse[list[PromotionResponse]])
async def list_promotions(admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/active", response_model=SuccessResponse[list[PromotionResponse]])
async def list_active_promotions(db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    return SuccessResponse(data=await service.get_active())


@router.get("/{promotion_id}", response_model=SuccessResponse[PromotionResponse])
async def get_promotion(promotion_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    return SuccessResponse(data=await service.get_by_id(promotion_id))


@router.post("", response_model=SuccessResponse[PromotionResponse])
async def create_promotion(data: PromotionCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    return SuccessResponse(data=await service.create(data), message="Promotion created")


@router.put("/{promotion_id}", response_model=SuccessResponse[PromotionResponse])
async def update_promotion(promotion_id: int, data: PromotionUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    return SuccessResponse(data=await service.update(promotion_id, data), message="Promotion updated")


@router.delete("/{promotion_id}", response_model=SuccessResponse)
async def delete_promotion(promotion_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = PromotionService(db)
    await service.delete(promotion_id)
    return SuccessResponse(message="Promotion deleted")
