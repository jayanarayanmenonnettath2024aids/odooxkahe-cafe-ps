"""
Authentication router — signup, login, refresh, me.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=SuccessResponse[UserResponse])
async def signup(data: SignupRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.signup(data)
    return SuccessResponse(data=user, message="User registered successfully")


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(current_user = Depends(CurrentUser)):
    return SuccessResponse(data=UserResponse.model_validate(current_user))
