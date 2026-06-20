"""
Tables router — CRUD + by-floor + status.
"""

import io
from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import AdminUser
from app.schemas.common import SuccessResponse
from app.schemas.table import TableCreate, TableResponse, TableUpdate
from app.services.table_service import TableService

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("", response_model=SuccessResponse[list[TableResponse]])
async def list_tables(db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_all())


@router.get("/status", response_model=SuccessResponse[list[TableResponse]])
async def get_table_status(db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_status_summary())


@router.get("/by-floor/{floor_id}", response_model=SuccessResponse[list[TableResponse]])
async def get_tables_by_floor(floor_id: int, db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_by_floor(floor_id))


@router.get("/bulk-qr")
async def bulk_qr_pdf(admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    # Generate a dummy bulk QR PDF for testing purposes
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Bulk Table QRs")
    c.save()
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=bulk_qr.pdf"})

@router.get("/{table_id}", response_model=SuccessResponse[TableResponse])
async def get_table(table_id: int, db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.get_by_id(table_id))


@router.get("/{table_id}/qr-pdf")
async def get_table_qr_pdf(table_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    table = await service.get_by_id(table_id)
    # Generate a dummy QR PDF for testing purposes
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, f"Table QR: {table.table_number}")
    c.drawString(100, 730, f"Token: {table.unique_token}")
    c.save()
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=table_{table_id}_qr.pdf"})

@router.post("", response_model=SuccessResponse[TableResponse])
async def create_table(data: TableCreate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.create(data), message="Table created")


@router.put("/{table_id}", response_model=SuccessResponse[TableResponse])
async def update_table(table_id: int, data: TableUpdate, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    return SuccessResponse(data=await service.update(table_id, data), message="Table updated")


@router.delete("/{table_id}", response_model=SuccessResponse)
async def delete_table(table_id: int, admin = Depends(AdminUser), db: AsyncSession = Depends(get_db)):
    service = TableService(db)
    await service.delete(table_id)
    return SuccessResponse(message="Table deleted")
