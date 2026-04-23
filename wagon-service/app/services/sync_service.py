from __future__ import annotations

import time
import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories.sync_log_repo import SyncLogRepository
from app.schemas.sync_status import SourceStatus, SyncStatusResponse

log = structlog.get_logger(__name__)

# Идентификаторы источников, используемые в sync_log.source
_SOURCES = ("rwl", "onec")


class SyncService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = SyncLogRepository(session)

    # ------------------------------------------------------------------
    # Статус
    # ------------------------------------------------------------------

    async def get_status(self) -> SyncStatusResponse:
        logs = await self._repo.get_all()
        return SyncStatusResponse(
            sources=[
                SourceStatus(
                    source=log.source,
                    last_success_at=log.last_success_at,
                    last_status=log.last_status,
                    last_error=log.last_error,
                )
                for log in logs
            ]
        )

    # ------------------------------------------------------------------
    # Синхронизация
    # ------------------------------------------------------------------

    async def run_sync(self) -> dict[str, str]:
        """Запустить синхронизацию из всех источников.

        Каждый источник обрабатывается независимо: сбой одного
        не прерывает обработку остального.

        Возвращает словарь ``{source: status}`` для удобства триггер-эндпоинта.
        """
        results: dict[str, str] = {}
        for source in _SOURCES:
            results[source] = await self._sync_source(source)
        return results

    async def _sync_source(self, source: str) -> str:
        """Синхронизировать один источник; вернуть итоговый статус."""
        await self._repo.upsert_running(source)
        t0 = time.monotonic()
        try:
            if source == "rwl":
                await self._sync_rwl()
            elif source == "onec":
                await self._sync_onec()

            duration_ms = int((time.monotonic() - t0) * 1000)
            await self._repo.upsert_success(source)
            log.info("sync_service.source_ok", source=source, duration_ms=duration_ms)
            return "success"
        except Exception as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            error_text = str(exc)
            await self._repo.upsert_error(source, error_text)
            log.error(
                "sync_service.source_error",
                source=source,
                duration_ms=duration_ms,
                error=error_text,
            )
            return "error"

    async def _sync_rwl(self) -> None:
        from app.integrations.rwl_client import RwlClient

        client = RwlClient()
        wagons = await client.fetch_wagons()
        log.info("sync_service.rwl_fetched", count=len(wagons))
        # Сохранение/обновление вагонов в БД будет добавлено отдельной задачей

    async def _sync_onec(self) -> None:
        from app.integrations.onec_client import OneCClient

        client = OneCClient()
        requests = await client.fetch_requests()
        log.info("sync_service.onec_fetched", count=len(requests))
        # Сохранение/обновление заявок в БД будет добавлено отдельной задачей


# ------------------------------------------------------------------
# Точка входа для планировщика (не требует HTTP-контекста)
# ------------------------------------------------------------------

async def run_sync_job(session_factory: async_sessionmaker[AsyncSession]) -> None:
    """Корутина, запускаемая планировщиком и ручным триггером."""
    log.info("sync_job.started")
    async with session_factory() as session:
        results = await SyncService(session).run_sync()
    log.info("sync_job.finished", results=results)
