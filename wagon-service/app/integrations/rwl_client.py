from __future__ import annotations

import httpx
import structlog

from app.config import settings
from app.integrations.base import AbstractSourceClient, WagonRaw

log = structlog.get_logger(__name__)


class RwlClient(AbstractSourceClient):
    """HTTP-клиент для интеграции с системой RWL.

    Поддерживает пагинацию: запрашивает страницы по 500 вагонов
    до тех пор, пока ответ содержит ``has_more=true``.
    """

    def __init__(self) -> None:
        self._base_url = settings.rwl_base_url
        self._headers = {"X-Api-Key": settings.rwl_api_key}

    async def fetch_wagons(self) -> list[WagonRaw]:
        timeout = httpx.Timeout(30.0, connect=10.0)
        wagons: list[WagonRaw] = []
        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=timeout,
        ) as client:
            page = 1
            while True:
                resp = await client.get(
                    "/wagons", params={"page": page, "per_page": 500}
                )
                resp.raise_for_status()
                data = resp.json()
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    wagons.append(self._normalize(item))
                if not data.get("has_more", False):
                    break
                page += 1

        log.info("rwl_client.fetch_wagons.done", count=len(wagons))
        return wagons

    def _normalize(self, item: dict) -> WagonRaw:
        return WagonRaw(
            external_id_rwl=str(item["id"]),
            number=item["wagon_number"],
            owner_type=item.get("owner_type", "unknown"),
            wagon_type=item.get("wagon_type", "unknown"),
            model=item.get("model"),
            capacity_tons=item.get("capacity_tons"),
            volume_m3=item.get("volume_m3"),
            current_country=item.get("current_country"),
            current_station_code=item.get("station_code"),
            current_station_name=item.get("station_name"),
            current_city=item.get("city"),
            status=item.get("status", "unknown"),
            source="RWL",
        )
