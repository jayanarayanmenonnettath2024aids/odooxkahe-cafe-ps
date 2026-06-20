"""
Authentication service — signup, login, JWT token management.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)

    async def signup(self, data: SignupRequest) -> UserResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise AlreadyExistsException("User", "email", data.email)

        user = await self.user_repo.create({
            "name": data.name,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "role": data.role,
        })
        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # Store in DB
        payload = decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        await self.refresh_repo.create({
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": expires_at,
        })

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid refresh token")
                
            # Verify token in DB
            db_token = await self.refresh_repo.get_by_token(refresh_token)
            if not db_token or db_token.revoked:
                raise UnauthorizedException("Token has been revoked or is invalid")
                
            sub_val = payload.get("sub")
            if not sub_val:
                raise UnauthorizedException("Invalid token payload")
            user_id = int(sub_val)
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                raise UnauthorizedException("User not found or inactive")
        except Exception:
            raise UnauthorizedException("Invalid refresh token")

        # Revoke old token
        await self.refresh_repo.revoke_token(refresh_token)

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})

        # Store new token
        new_payload = decode_token(new_refresh_token)
        new_expires = datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc)
        await self.refresh_repo.create({
            "user_id": user.id,
            "token": new_refresh_token,
            "expires_at": new_expires,
        })

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(self, refresh_token: str) -> None:
        """Revoke a specific refresh token."""
        await self.refresh_repo.revoke_token(refresh_token)
