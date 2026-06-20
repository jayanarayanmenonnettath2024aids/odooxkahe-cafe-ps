"""
Reservations router — Smart booking, Twilio integration hooks, standard CRUD.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import EmployeeUser
from app.schemas.common import SuccessResponse
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
    TableRecommendationRequest,
)
from app.schemas.table import TableResponse
from app.services.reservation_service import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("/", response_model=SuccessResponse[ReservationResponse])
async def create_reservation(
    data: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    # Optional dependency: We might want public users to create reservations, but for now Employee only,
    # or no auth for public reservation endpoint if we separate it. Let's make it Employee only for now.
    user=Depends(EmployeeUser),
):
    service = ReservationService(db)
    reservation = await service.create(data)
    return SuccessResponse(data=reservation, message="Reservation created successfully")


@router.get("/", response_model=SuccessResponse[List[ReservationResponse]])
async def list_reservations(
    user=Depends(EmployeeUser), db: AsyncSession = Depends(get_db)
):
    service = ReservationService(db)
    reservations = await service.get_all()
    return SuccessResponse(data=reservations)


@router.get("/{id}", response_model=SuccessResponse[ReservationResponse])
async def get_reservation(
    id: int, user=Depends(EmployeeUser), db: AsyncSession = Depends(get_db)
):
    service = ReservationService(db)
    reservation = await service.get_by_id(id)
    return SuccessResponse(data=reservation)


@router.get("/{id}/pdf")
async def get_reservation_pdf(
    id: int, user=Depends(EmployeeUser), db: AsyncSession = Depends(get_db)
):
    from fastapi import Response
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from app.utils.qr import generate_qr_bytes
    from reportlab.lib.utils import ImageReader
    
    service = ReservationService(db)
    reservation = await service.get_by_id(id)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 750, f"Reservation Confirmation: #{reservation.id}")
    c.setFont("Helvetica", 12)
    c.drawString(150, 720, f"Customer: {reservation.customer_name}")
    c.drawString(150, 700, f"Date: {reservation.reservation_date.strftime('%Y-%m-%d')}")
    c.drawString(150, 680, f"Time: {reservation.reservation_time.strftime('%H:%M')}")
    c.drawString(150, 660, f"Guests: {reservation.guest_count}")
    
    qr_url = f"https://cafepos.app/reservations/checkin/{reservation.id}"
    qr_bytes = generate_qr_bytes(qr_url)
    img = ImageReader(io.BytesIO(qr_bytes))
    c.drawImage(img, 150, 450, width=80*mm, height=80*mm)
    c.setFont("Helvetica", 10)
    c.drawString(150, 430, "Scan this QR code upon arrival for quick check-in")
    
    c.save()
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=reservation_{id}.pdf"})


@router.patch("/{id}", response_model=SuccessResponse[ReservationResponse])
async def update_reservation(
    id: int,
    data: ReservationUpdate,
    user=Depends(EmployeeUser),
    db: AsyncSession = Depends(get_db),
):
    service = ReservationService(db)
    reservation = await service.update(id, data)
    return SuccessResponse(data=reservation, message="Reservation updated successfully")


@router.post("/recommend-table", response_model=SuccessResponse[List[TableResponse]])
async def recommend_table(
    data: TableRecommendationRequest, db: AsyncSession = Depends(get_db)
):
    """Smart recommendation engine: Finds smallest available tables for the requested slot."""
    service = ReservationService(db)
    tables = await service.recommend_table(data)
    return SuccessResponse(data=tables)
