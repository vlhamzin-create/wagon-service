from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.nsi_loader.etran.xml_parsers import parse_cargos
from app.nsi_loader.jobs.base_job import BaseNsiJob
from app.nsi_loader.repository.cargo_repo import CargoNsiRepository


class CargosJob(BaseNsiJob):
    dictionary_name = "cargos"
    nsi_type = "CargoList"

    def parse(self, xml_text: str) -> Sequence[BaseModel]:
        return parse_cargos(xml_text)

    async def save(self, session: AsyncSession, records: Sequence[BaseModel]) -> int:
        repo = CargoNsiRepository(session)
        return await repo.upsert_cargos(records)  # type: ignore[arg-type]
