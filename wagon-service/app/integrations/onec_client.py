from __future__ import annotations

import httpx

from app.config import settings
from app.integrations.base import BaseIntegrationClient


class OneCClient(BaseIntegrationClient):
    """HTTP-клиент для интеграции с 1С."""

    async def fetch_wagons(self) -> list[dict]:
        async with httpx.AsyncClient(
            base_url=settings.onec_base_url,
            auth=(settings.onec_login, settings.onec_password),
            timeout=30,
        ) as client:
            response = await client.get("/wagons")
            response.raise_for_status()
            return response.json()
