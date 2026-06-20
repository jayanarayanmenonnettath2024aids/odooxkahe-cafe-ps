"""
Payment processing schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.payment import PaymentStatus


class CashPaymentRequest(BaseModel):
    order_id: int
    received_amount: float = Field(..., gt=0)


class CashPaymentResponse(BaseModel):
    order_id: int
    total_amount: float
    received_amount: float
    change_due: float
    payment_status: PaymentStatus
    receipt_url: Optional[str] = None


class UPIPaymentRequest(BaseModel):
    order_id: int


class UPIPaymentResponse(BaseModel):
    order_id: int
    total_amount: float
    qr_image_url: str
    upi_deeplink: str
    payment_id: int


class UPIConfirmRequest(BaseModel):
    payment_id: int
    transaction_reference: str


class CardPaymentRequest(BaseModel):
    order_id: int
    transaction_reference: str


class CardPaymentResponse(BaseModel):
    order_id: int
    total_amount: float
    transaction_reference: str
    payment_status: PaymentStatus
    receipt_url: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method_id: int
    payment_method_name: Optional[str] = None
    amount: float
    transaction_reference: Optional[str] = None
    status: PaymentStatus

    model_config = {"from_attributes": True}
