from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings

logger = structlog.get_logger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _sync_job() -> None:
    """Фоновая задача синхронизации данных вагонов из внешних систем."""
    from app.database import AsyncSessionLocal
    from app.repositories.sync_log_repo import SyncLogRepository

    logger.info("sync_job.started")
    async with AsyncSessionLocal() as session:
        repo = SyncLogRepository(session)
        for source in ("rwl", "onec"):
            try:
                # Реальная синхронизация реализуется в соответствующих клиентах
                await repo.upsert(source=source, last_status="ok")
                logger.info("sync_job.source_ok", source=source)
            except Exception as exc:
                await repo.upsert(source=source, last_status="error", last_error=str(exc))
                logger.error("sync_job.source_error", source=source, error=str(exc))
    logger.info("sync_job.finished")


def create_scheduler() -> AsyncIOScheduler:
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _sync_job,
        trigger=IntervalTrigger(minutes=settings.sync_interval_minutes),
        id="sync_wagons",
        replace_existing=True,
    )
    return _scheduler


def get_scheduler() -> AsyncIOScheduler | None:
    return _scheduler
