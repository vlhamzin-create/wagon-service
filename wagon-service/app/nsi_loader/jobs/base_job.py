from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Sequence

import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.nsi_loader.config import NsiLoaderConfig
from app.nsi_loader.etran.nsi_client import NsiClient
from app.nsi_loader.repository.sync_state_repo import SyncStateRepository

log = structlog.get_logger(__name__)


class BaseNsiJob(ABC):
    """Абстрактный джоб синхронизации одного НСИ-справочника."""

    dictionary_name: str
    nsi_type: str

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        config: NsiLoaderConfig,
    ) -> None:
        self._session_factory = session_factory
        self._config = config
        self._nsi_client = NsiClient(config)

    async def run(self) -> None:
        async with self._session_factory() as session:
            sync_repo = SyncStateRepository(session)

            await sync_repo.set_running(self.dictionary_name)
            t0 = time.monotonic()

            try:
                state = await sync_repo.get(self.dictionary_name)
                chg_dt = state.last_chg_dt if state else None

                xml_text = await self._nsi_client.fetch_nsi(
                    self.nsi_type, chg_date_time=chg_dt
                )

                records = self.parse(xml_text)
                upserted = await self.save(session, records)

                new_chg_dt = self._extract_chg_dt(xml_text, chg_dt)
                duration_ms = int((time.monotonic() - t0) * 1000)

                await sync_repo.set_success(
                    self.dictionary_name,
                    records_total=len(records),
                    records_upserted=upserted,
                    last_chg_dt=new_chg_dt,
                )

                log.info(
                    "nsi_job.success",
                    dictionary=self.dictionary_name,
                    total=len(records),
                    upserted=upserted,
                    duration_ms=duration_ms,
                    incremental=chg_dt is not None,
                )
            except Exception as exc:
                duration_ms = int((time.monotonic() - t0) * 1000)
                log.error(
                    "nsi_job.error",
                    dictionary=self.dictionary_name,
                    error=str(exc),
                    duration_ms=duration_ms,
                )
                await sync_repo.set_error(self.dictionary_name, str(exc))

    @abstractmethod
    def parse(self, xml_text: str) -> Sequence[BaseModel]:
        ...

    @abstractmethod
    async def save(self, session: AsyncSession, records: Sequence[BaseModel]) -> int:
        ...

    def _extract_chg_dt(self, xml_text: str, fallback: str | None) -> str | None:
        """Извлекает ChgDateTime из XML-ответа для следующего инкрементального запроса."""
        from lxml import etree

        try:
            root = etree.fromstring(xml_text.encode("utf-8"))  # noqa: S320
            el = root.find(".//ChgDateTime")
            if el is not None and el.text:
                return el.text.strip()
        except Exception:
            pass
        return fallback
