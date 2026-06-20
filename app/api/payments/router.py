"""
Payment processing router — cash, UPI, card.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.common import SuccessResponse
from app.schemas.payment import (
    CardPaymentRequest,
    CardPaymentResponse,
    CashPaymentRequest,
    CashPaymentResponse,
    UPIConfirmRequest,
    UPIPaymentRequest,
    UPIPaymentResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payment", tags=["Payments"])


@router.post("/cash", response_model=SuccessResponse[CashPaymentResponse])
async def pay_cash(data: CashPaymentRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = PaymentService(db)
    result = await service.process_cash_payment(data)
    return SuccessResponse(data=result, message="Cash payment processed")


@router.post("/upi", response_model=SuccessResponse[UPIPaymentResponse])
async def pay_upi(data: UPIPaymentRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = PaymentService(db)
    result = await service.process_upi_payment(data)
    return SuccessResponse(data=result, message="UPI QR generated")


@router.post("/upi/confirm", response_model=SuccessResponse[CashPaymentResponse])
async def confirm_upi(data: UPIConfirmRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = PaymentService(db)
    result = await service.confirm_upi_payment(data)
    return SuccessResponse(data=result, message="UPI payment confirmed")


@router.post("/card", response_model=SuccessResponse[CardPaymentResponse])
async def pay_card(data: CardPaymentRequest, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = PaymentService(db)
    result = await service.process_card_payment(data)
    return SuccessResponse(data=result, message="Card payment processed")
