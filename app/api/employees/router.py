"""
Employees router — CRUD, archive, change password.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser, CurrentUser
from app.schemas.common import SuccessResponse
from app.schemas.employee import ChangePasswordRequest, EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=SuccessResponse[list[EmployeeResponse]])
async def list_employees(admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/{employee_id}", response_model=SuccessResponse[EmployeeResponse])
async def get_employee(employee_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return SuccessResponse(data=await service.get_by_id(employee_id))


@router.post("", response_model=SuccessResponse[EmployeeResponse])
async def create_employee(data: EmployeeCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return SuccessResponse(data=await service.create(data), message="Employee created")


@router.put("/{employee_id}", response_model=SuccessResponse[EmployeeResponse])
async def update_employee(employee_id: int, data: EmployeeUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return SuccessResponse(data=await service.update(employee_id, data), message="Employee updated")


@router.patch("/{employee_id}/archive", response_model=SuccessResponse[EmployeeResponse])
async def archive_employee(employee_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    return SuccessResponse(data=await service.archive(employee_id), message="Employee archived")


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(data: ChangePasswordRequest, current_user = Depends(CurrentUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    await service.change_password(current_user.id, data)
    return SuccessResponse(message="Password changed successfully")


@router.delete("/{employee_id}", response_model=SuccessResponse)
async def delete_employee(employee_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = EmployeeService(db)
    await service.delete(employee_id)
    return SuccessResponse(message="Employee deleted")
