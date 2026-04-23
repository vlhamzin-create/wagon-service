from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dicts import WagonTypeDict
from app.nsi_loader.models.wagon_type import WagonTypeRecord
from app.nsi_loader.repository.base import BaseNsiRepository

_UPDATE_COLS = [
    "type_name", "cargo_capacity", "volume", "tare_weight",
    "axle_count", "is_active", "etran_version",
]


class WagonTypeNsiRepository(BaseNsiRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WagonTypeDict.__table__, "type_code")

    async def upsert_wagon_types(self, records: Sequence[WagonTypeRecord]) -> int:
        return await self.upsert_batch(records, _UPDATE_COLS)
