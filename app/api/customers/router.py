"""
Customers router — CRUD + search.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.common import SuccessResponse
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=SuccessResponse[list[CustomerResponse]])
async def list_customers(
    search: Optional[str] = Query(None),
    user = Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = CustomerService(db)
    if search:
        return SuccessResponse(data=await service.search(search))
    return SuccessResponse(data=await service.get_all())


@router.get("/{customer_id}", response_model=SuccessResponse[CustomerResponse])
async def get_customer(customer_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    return SuccessResponse(data=await service.get_by_id(customer_id))


@router.post("", response_model=SuccessResponse[CustomerResponse])
async def create_customer(data: CustomerCreate, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    return SuccessResponse(data=await service.create(data), message="Customer created")


@router.put("/{customer_id}", response_model=SuccessResponse[CustomerResponse])
async def update_customer(customer_id: int, data: CustomerUpdate, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    return SuccessResponse(data=await service.update(customer_id, data), message="Customer updated")


@router.delete("/{customer_id}", response_model=SuccessResponse)
async def delete_customer(customer_id: int, user = Depends(EmployeeUser), db: AsyncSession = Depends(get_db)):
    service = CustomerService(db)
    await service.delete(customer_id)
    return SuccessResponse(message="Customer deleted")
