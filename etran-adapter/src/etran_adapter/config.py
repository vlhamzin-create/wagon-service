from __future__ import annotations

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ЭТРАН
    etran_wsdl_url: AnyHttpUrl | None = None
    etran_endpoint_url: AnyHttpUrl
    etran_login: str
    etran_password: SecretStr
    etran_asu_go_id: str
    etran_timeout_seconds: int = 60
    etran_max_retries: int = 3

    # Асинхронный путь
    redis_url: str = "redis://localhost:6379/0"
    rq_queue_name: str = "etran"
    rq_high_queue_name: str = "etran_high"
    task_result_ttl_seconds: int = 3600

    # БД
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/etran_adapter"

    # Безопасность (internal API key для wagon-service)
    internal_api_key: SecretStr

    # Callback
    wagon_service_callback_url: AnyHttpUrl | None = None

    # Прочее
    log_level: str = "INFO"


settings = Settings()
