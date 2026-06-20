"""
Payment method schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field


class PaymentMethodCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    enabled: bool = True
    upi_id: Optional[str] = None


class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    enabled: Optional[bool] = None
    upi_id: Optional[str] = None


class PaymentMethodResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    upi_id: Optional[str] = None

    model_config = {"from_attributes": True}
