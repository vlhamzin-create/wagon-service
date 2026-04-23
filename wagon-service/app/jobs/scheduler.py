from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings

log = structlog.get_logger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _sync_job() -> None:
    """Фоновая задача: синхронизация данных из RWL и 1С."""
    from app.database import AsyncSessionLocal
    from app.services.sync_service import run_sync_job

    await run_sync_job(AsyncSessionLocal)


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
