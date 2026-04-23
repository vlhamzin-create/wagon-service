from __future__ import annotations

import httpx

from app.config import settings
from app.integrations.base import BaseIntegrationClient


class RwlClient(BaseIntegrationClient):
    """HTTP-клиент для интеграции с системой РЖД/RWL."""

    async def fetch_wagons(self) -> list[dict]:
        async with httpx.AsyncClient(
            base_url=settings.rwl_base_url,
            headers={"X-Api-Key": settings.rwl_api_key},
            timeout=30,
        ) as client:
            response = await client.get("/wagons")
            response.raise_for_status()
            return response.json()
