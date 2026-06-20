"""
Reservation service — CRUD and Smart Recommendation Engine.
"""

from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.table import TableStatus
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.table_repository import TableRepository
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
    TableRecommendationRequest,
)
from app.schemas.table import TableResponse


class ReservationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReservationRepository(db)
        self.table_repo = TableRepository(db)

    async def create(self, data: ReservationCreate) -> ReservationResponse:
        # Validate table capacity and overlap if table is specified
        if data.table_id:
            table = await self.table_repo.get_by_id(data.table_id)
            if not table:
                raise NotFoundException("Table", data.table_id)
            if table.seat_count < data.guest_count:
                raise BadRequestException(
                    f"Table {data.table_id} capacity ({table.seat_count}) is less than guest count ({data.guest_count})"
                )

            overlap = await self.repo.check_overlap(
                data.table_id, data.reservation_date, data.start_time, data.end_time
            )
            if overlap:
                raise BadRequestException("Table is already reserved for this time slot.")

        reservation = await self.repo.create(data.model_dump())
        return ReservationResponse.model_validate(reservation)

    async def get_by_id(self, id: int) -> ReservationResponse:
        reservation = await self.repo.get_by_id(id)
        if not reservation:
            raise NotFoundException("Reservation", id)
        return ReservationResponse.model_validate(reservation)

    async def get_all(self, for_date: date | None = None) -> list[ReservationResponse]:
        reservations = await self.repo.get_all(for_date)
        return [ReservationResponse.model_validate(r) for r in reservations]

    async def update(self, id: int, data: ReservationUpdate) -> ReservationResponse:
        reservation = await self.repo.get_by_id(id)
        if not reservation:
            raise NotFoundException("Reservation", id)
            
        update_data = data.model_dump(exclude_unset=True)
        
        # If updating table, check for overlap
        new_table_id = update_data.get("table_id", reservation.table_id)
        if new_table_id:
            overlap = await self.repo.check_overlap(
                new_table_id, 
                reservation.reservation_date, 
                reservation.start_time, 
                reservation.end_time,
                exclude_id=reservation.id
            )
            if overlap:
                raise BadRequestException("Table is already reserved for this time slot.")

        updated = await self.repo.update(id, update_data)
        if not updated:
            raise NotFoundException("Reservation", id)
        return ReservationResponse.model_validate(updated)

    async def recommend_table(self, data: TableRecommendationRequest) -> list[TableResponse]:
        """
        Smart Recommendation Engine:
        Find smallest available tables where capacity >= guest_count
        and it's not reserved for the requested time.
        """
        all_tables = await self.table_repo.get_all_with_status()
        
        # Filter tables with enough capacity
        suitable_tables = [t for t in all_tables if t.seat_count >= data.guest_count and t.active_status != TableStatus.OCCUPIED]
        
        available_tables = []
        for table in suitable_tables:
            # Check overlap
            overlap = await self.repo.check_overlap(
                table.id, data.reservation_date, data.start_time, data.end_time
            )
            if not overlap:
                available_tables.append(table)
                
        # Sort by seat count ascending (smallest suitable table first)
        available_tables.sort(key=lambda t: t.seat_count)
        
        return [TableResponse(
            id=t.id,
            floor_id=t.floor_id,
            floor_name=t.floor.name if t.floor else None,
            table_number=t.table_number,
            seat_count=t.seat_count,
            active_status=t.active_status,
            unique_token=t.unique_token,
        ) for t in available_tables]
