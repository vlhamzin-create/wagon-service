from __future__ import annotations

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.nsi_loader.config import nsi_config

log = structlog.get_logger(__name__)


async def _run_stations_job() -> None:
    from app.database import AsyncSessionLocal
    from app.nsi_loader.jobs.stations_job import StationsJob

    job = StationsJob(AsyncSessionLocal, nsi_config)
    await job.run()


async def _run_wagon_types_job() -> None:
    from app.database import AsyncSessionLocal
    from app.nsi_loader.jobs.wagons_job import WagonTypesJob

    job = WagonTypesJob(AsyncSessionLocal, nsi_config)
    await job.run()


async def _run_cargos_job() -> None:
    from app.database import AsyncSessionLocal
    from app.nsi_loader.jobs.cargos_job import CargosJob

    job = CargosJob(AsyncSessionLocal, nsi_config)
    await job.run()


def register_nsi_jobs(scheduler: AsyncIOScheduler) -> None:
    """Регистрирует джобы загрузки НСИ-справочников в планировщике."""
    if not nsi_config.sync_enabled:
        log.info("nsi_scheduler.disabled")
        return

    scheduler.add_job(
        _run_stations_job,
        trigger=CronTrigger(hour=nsi_config.stations_cron_hour, minute=0),
        id="nsi_sync_stations",
        replace_existing=True,
    )

    scheduler.add_job(
        _run_wagon_types_job,
        trigger=IntervalTrigger(hours=nsi_config.wagon_types_interval_hours),
        id="nsi_sync_wagon_types",
        replace_existing=True,
    )

    scheduler.add_job(
        _run_cargos_job,
        trigger=CronTrigger(hour=nsi_config.cargos_cron_hour, minute=30),
        id="nsi_sync_cargos",
        replace_existing=True,
    )

    log.info(
        "nsi_scheduler.registered",
        stations_cron_hour=nsi_config.stations_cron_hour,
        wagon_types_interval_h=nsi_config.wagon_types_interval_hours,
        cargos_cron_hour=nsi_config.cargos_cron_hour,
    )
