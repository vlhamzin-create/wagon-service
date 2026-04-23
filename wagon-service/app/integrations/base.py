from __future__ import annotations

from abc import ABC, abstractmethod


class BaseIntegrationClient(ABC):
    """Базовый контракт для клиентов внешних систем."""

    @abstractmethod
    async def fetch_wagons(self) -> list[dict]:
        """Получить список вагонов из внешней системы."""
