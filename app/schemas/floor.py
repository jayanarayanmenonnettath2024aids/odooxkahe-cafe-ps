"""
Floor schemas.
"""

from typing import Optional

from pydantic import BaseModel, Field


class FloorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class FloorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class FloorResponse(BaseModel):
    id: int
    name: str
    table_count: int = 0

    model_config = {"from_attributes": True}
