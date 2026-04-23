from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CargoRecord(BaseModel):
    etsng_code: str = Field(..., max_length=16)
    etsng_name: str = Field(..., max_length=255)
    gng_code: Optional[str] = Field(None, max_length=16)
    gng_name: Optional[str] = Field(None, max_length=255)
    cargo_group: Optional[str] = Field(None, max_length=64)
    is_dangerous: bool = False
    is_active: bool = True
    etran_version: Optional[int] = None
