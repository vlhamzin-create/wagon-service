from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.nsi_loader.etran.xml_parsers import parse_wagon_types
from app.nsi_loader.jobs.base_job import BaseNsiJob
from app.nsi_loader.repository.wagon_type_repo import WagonTypeNsiRepository


class WagonTypesJob(BaseNsiJob):
    dictionary_name = "wagon_types"
    nsi_type = "WagonNSI"

    def parse(self, xml_text: str) -> Sequence[BaseModel]:
        return parse_wagon_types(xml_text)

    async def save(self, session: AsyncSession, records: Sequence[BaseModel]) -> int:
        repo = WagonTypeNsiRepository(session)
        return await repo.upsert_wagon_types(records)  # type: ignore[arg-type]
