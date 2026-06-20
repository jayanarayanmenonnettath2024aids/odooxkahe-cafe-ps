"""
Employee schemas.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.EMPLOYEE


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
