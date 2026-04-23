from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class WagonFilters(BaseModel):
    mode: Literal["all", "requires_assignment"] = "all"
    owner_type: list[str] | None = None
    wagon_type: list[str] | None = None
    status: list[str] | None = None
    destination_railway: list[str] | None = None
    supplier_name: list[str] | None = None
    current_city: list[str] | None = None
    current_station_name: list[str] | None = None
    search: str | None = None
    # Сортировка по умолчанию соответствует idx_wagon_sort_default
    sort_by: str = "destination_railway"
    sort_dir: Literal["asc", "desc"] = "desc"
    limit: int = 100
    offset: int = 0

    @field_validator("limit")
    @classmethod
    def cap_limit(cls, v: int) -> int:
        return min(v, 100)


class WagonListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    number: str
    owner_type: str
    wagon_type: str
    current_country: str | None
    current_station_code: str | None
    current_station_name: str | None
    current_city: str | None
    destination_station_name: str | None
    destination_railway: str | None
    next_destination_station_name: str | None
    days_without_movement: int | None
    supplier_name: str | None
    status: str
    requires_assignment: bool
    source: str
    updated_at: datetime


class WagonDetail(WagonListItem):
    external_id_rwl: str
    model: str | None
    capacity_tons: float | None
    volume_m3: float | None
    last_movement_at: datetime | None
    created_at: datetime


class PaginatedWagons(BaseModel):
    items: list[WagonListItem]
    total: int
    limit: int
    offset: int
    has_more: bool


class FilterOption(BaseModel):
    value: str
    label: str


class FilterOptionsResponse(BaseModel):
    destination_railway: list[FilterOption]
    supplier_name: list[FilterOption]
    current_city: list[FilterOption]
    owner_type: list[FilterOption]
    wagon_type: list[FilterOption]
    status: list[FilterOption]
