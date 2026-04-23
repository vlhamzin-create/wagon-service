from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class StationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    country: str | None


class StationsResponse(BaseModel):
    items: list[StationItem]
    total: int
