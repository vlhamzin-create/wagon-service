from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator


class AssignRouteRequest(BaseModel):
    wagon_ids: list[uuid.UUID]
    station_code: str | None = None
    client_id: uuid.UUID | None = None
    overwrite: bool = False

    @field_validator("wagon_ids")
    @classmethod
    def wagon_ids_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("wagon_ids не может быть пустым")
        if len(v) > 200:
            raise ValueError("Максимум 200 вагонов за один запрос")
        return v

    @model_validator(mode="after")
    def at_least_one_target(self) -> AssignRouteRequest:
        if self.station_code is None and self.client_id is None:
            raise ValueError("Необходимо указать station_code или client_id")
        return self


class WagonAssignResult(BaseModel):
    wagon_id: uuid.UUID
    status: Literal["ok", "skipped", "error"]
    reason: str | None = None


class AssignRouteResponse(BaseModel):
    total: int
    succeeded: int
    skipped: int
    failed: int
    results: list[WagonAssignResult]
