from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # БД
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/wagon_service"

    # JWT
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "wagon-service"

    # Внешние системы
    rwl_base_url: str = "http://rwl-service"
    rwl_api_key: str = ""
    onec_base_url: str = "http://onec-service"
    onec_login: str = ""
    onec_password: str = ""

    # Синхронизация
    sync_interval_minutes: int = 60

    # Интеграция с 1С: отправка назначений
    onec_assignment_url: str = ""  # URL эндпоинта 1С для приёма назначений
    onec_assignment_timeout: float = 10.0
    onec_assignment_max_retries: int = 5
    onec_assignment_retry_base_seconds: int = 60  # 1 мин → 2 → 4 → 8 → 16

    # НСИ ЭТРАН
    etran_adapter_url: str = "http://etran-adapter"
    etran_adapter_api_key: str = ""
    etran_adapter_timeout: float = 30.0
    nsi_stations_cron_hour: int = 3
    nsi_wagon_types_interval_hours: int = 4
    nsi_cargos_cron_hour: int = 4
    nsi_sync_enabled: bool = True

    # Прочее
    log_level: str = "INFO"
    allowed_roles: list[str] = ["Руководитель", "Логист", "Просмотр", "Оператор", "Админ"]


settings = Settings()
