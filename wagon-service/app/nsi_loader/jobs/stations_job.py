from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.nsi_loader.etran.xml_parsers import parse_stations
from app.nsi_loader.jobs.base_job import BaseNsiJob
from app.nsi_loader.repository.station_repo import StationNsiRepository


class StationsJob(BaseNsiJob):
    dictionary_name = "stations"
    nsi_type = "StationList"

    def parse(self, xml_text: str) -> Sequence[BaseModel]:
        return parse_stations(xml_text)

    async def save(self, session: AsyncSession, records: Sequence[BaseModel]) -> int:
        repo = StationNsiRepository(session)
        return await repo.upsert_stations(records)  # type: ignore[arg-type]
