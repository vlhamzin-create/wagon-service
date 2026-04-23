from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class WagonTypeRecord(BaseModel):
    type_code: str = Field(..., max_length=16)
    type_name: str = Field(..., max_length=255)
    cargo_capacity: Optional[float] = None
    volume: Optional[float] = None
    tare_weight: Optional[float] = None
    axle_count: Optional[int] = None
    is_active: bool = True
    etran_version: Optional[int] = None
