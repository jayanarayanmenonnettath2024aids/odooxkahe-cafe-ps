"""
FastAPI dependency injection functions.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

security_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail=f"Invalid token type {payload.get('type')}")
        sub_val = payload.get("sub")
        if sub_val is None:
            raise HTTPException(status_code=401, detail="No user_id in token")
        user_id = int(sub_val)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"JWTError {e}")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail=f"User not found in DB! id={user_id}, user={user}")

    return user

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Required role(s): ['ADMIN']",
        )
    return current_user

async def get_employee_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.EMPLOYEE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Required role(s): ['ADMIN', 'EMPLOYEE']",
        )
    return current_user

# Keep aliases for backwards compatibility with imports
AdminUser = get_admin_user
EmployeeUser = get_employee_user
CurrentUser = get_current_user
