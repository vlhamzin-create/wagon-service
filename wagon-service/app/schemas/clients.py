from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict


class ClientItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    external_id_1c: str | None


class ClientsResponse(BaseModel):
    items: list[ClientItem]
    total: int
