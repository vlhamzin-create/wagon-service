from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dicts import StationDict
from app.nsi_loader.models.station import StationRecord
from app.nsi_loader.repository.base import BaseNsiRepository

_UPDATE_COLS = [
    "name", "short_name", "country_code", "country",
    "railway_code", "railway_name", "is_active", "etran_version",
]


class StationNsiRepository(BaseNsiRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StationDict.__table__, "code")

    async def upsert_stations(self, records: Sequence[StationRecord]) -> int:
        rows = []
        for r in records:
            d = r.model_dump()
            d["country"] = d.pop("country_name", None)
            rows.append(d)

        if not rows:
            return 0

        from pydantic import BaseModel

        class _Row(BaseModel):
            code: str
            name: str
            short_name: str | None = None
            country_code: str | None = None
            country: str | None = None
            railway_code: str | None = None
            railway_name: str | None = None
            is_active: bool = True
            etran_version: int | None = None

        return await self.upsert_batch(
            [_Row(**row) for row in rows],
            _UPDATE_COLS,
        )
