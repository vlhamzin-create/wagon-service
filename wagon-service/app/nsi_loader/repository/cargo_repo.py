from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dicts import CargoDict
from app.nsi_loader.models.cargo import CargoRecord
from app.nsi_loader.repository.base import BaseNsiRepository

_UPDATE_COLS = [
    "etsng_name", "gng_code", "gng_name", "cargo_group",
    "is_dangerous", "is_active", "etran_version",
]


class CargoNsiRepository(BaseNsiRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CargoDict.__table__, "etsng_code")

    async def upsert_cargos(self, records: Sequence[CargoRecord]) -> int:
        return await self.upsert_batch(records, _UPDATE_COLS)
