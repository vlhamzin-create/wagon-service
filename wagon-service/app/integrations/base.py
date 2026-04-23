from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WagonRaw:
    """Нормализованное представление вагона из любого источника."""

    external_id_rwl: str
    number: str
    owner_type: str
    wagon_type: str
    model: str | None
    capacity_tons: float | None
    volume_m3: float | None
    current_country: str | None
    current_station_code: str | None
    current_station_name: str | None
    current_city: str | None
    status: str
    source: str  # 'RWL' | '1C'


@dataclass
class RequestRaw:
    """Нормализованная заявка из 1С."""

    external_id_1c: str
    client_name: str
    required_wagon_type: str
    origin_station_code: str
    destination_station_code: str
    planned_date: str  # ISO date string
    status: str


class AbstractSourceClient(ABC):
    """Базовый контракт для клиентов внешних систем."""

    @abstractmethod
    async def fetch_wagons(self) -> list[WagonRaw]:
        """Получить список вагонов из источника."""
        ...

    async def fetch_requests(self) -> list[RequestRaw]:
        """Получить заявки (только 1С, у RWL нет)."""
        return []


# Обратная совместимость: псевдоним для старого имени
BaseIntegrationClient = AbstractSourceClient
