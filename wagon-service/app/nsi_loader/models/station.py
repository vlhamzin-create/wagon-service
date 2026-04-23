from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class StationRecord(BaseModel):
    code: str = Field(..., max_length=16)
    name: str = Field(..., max_length=255)
    short_name: Optional[str] = Field(None, max_length=64)
    country_code: Optional[str] = Field(None, max_length=8)
    country_name: Optional[str] = Field(None, max_length=128)
    railway_code: Optional[str] = Field(None, max_length=16)
    railway_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True
    etran_version: Optional[int] = None
