"""
JWT authentication and password hashing utilities.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(
    data: dict[str, Any],
    token_type: str,
    expires_delta: Optional[timedelta],
    default_expire_minutes: int,
) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=default_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": token_type, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    return _create_token(
        data, 
        token_type="access", 
        expires_delta=expires_delta, 
        default_expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    return _create_token(
        data, 
        token_type="refresh", 
        expires_delta=expires_delta, 
        default_expire_minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token. Raises JWTError on failure."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise
