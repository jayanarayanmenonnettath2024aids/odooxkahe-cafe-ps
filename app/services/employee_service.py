"""
Employee service — user management for employees.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AlreadyExistsException,
    BadRequestException,
    NotFoundException,
)
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.employee import (
    ChangePasswordRequest,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create(self, data: EmployeeCreate) -> EmployeeResponse:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise AlreadyExistsException("Employee", "email", data.email)

        user = await self.repo.create({
            "name": data.name,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "role": data.role,
        })
        return EmployeeResponse.model_validate(user)

    async def get_by_id(self, id: int) -> EmployeeResponse:
        user = await self.repo.get_by_id(id)
        if not user:
            raise NotFoundException("Employee", id)
        return EmployeeResponse.model_validate(user)

    async def get_all(self) -> list[EmployeeResponse]:
        users = await self.repo.get_active_employees()
        return [EmployeeResponse.model_validate(u) for u in users]

    async def update(self, id: int, data: EmployeeUpdate) -> EmployeeResponse:
        user = await self.repo.update(id, data.model_dump(exclude_unset=True))
        if not user:
            raise NotFoundException("Employee", id)
        return EmployeeResponse.model_validate(user)

    async def archive(self, id: int) -> EmployeeResponse:
        user = await self.repo.update(id, {"is_active": False})
        if not user:
            raise NotFoundException("Employee", id)
        return EmployeeResponse.model_validate(user)

    async def change_password(self, user_id: int, data: ChangePasswordRequest) -> bool:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Employee", user_id)

        if not verify_password(data.current_password, user.password_hash):
            raise BadRequestException("Current password is incorrect")

        user.password_hash = hash_password(data.new_password)
        await self.repo.db.flush()
        return True

    async def delete(self, id: int) -> bool:
        if not await self.repo.delete(id):
            raise NotFoundException("Employee", id)
        return True
