"""
Table schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.table import TableStatus


class TableCreate(BaseModel):
    floor_id: int
    table_number: str = Field(..., min_length=1, max_length=20)
    seat_count: int = Field(default=4, ge=1)


class TableUpdate(BaseModel):
    floor_id: Optional[int] = None
    table_number: Optional[str] = Field(None, min_length=1, max_length=20)
    seat_count: Optional[int] = Field(None, ge=1)
    active_status: Optional[TableStatus] = None


class TableResponse(BaseModel):
    id: int
    floor_id: int
    floor_name: Optional[str] = None
    table_number: str
    seat_count: int
    active_status: TableStatus
    unique_token: str

    model_config = {"from_attributes": True}


class TableSelectionResponse(BaseModel):
    """Response when an employee selects a table in POS."""
    table: TableResponse
    current_order: Optional[dict] = None
    table_status: TableStatus
