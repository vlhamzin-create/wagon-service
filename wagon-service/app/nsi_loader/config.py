from __future__ import annotations

from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class NsiLoaderConfig:
    etran_adapter_url: str = settings.etran_adapter_url
    etran_adapter_api_key: str = settings.etran_adapter_api_key
    etran_adapter_timeout: float = settings.etran_adapter_timeout
    stations_cron_hour: int = settings.nsi_stations_cron_hour
    wagon_types_interval_hours: int = settings.nsi_wagon_types_interval_hours
    cargos_cron_hour: int = settings.nsi_cargos_cron_hour
    sync_enabled: bool = settings.nsi_sync_enabled


nsi_config = NsiLoaderConfig()
