from __future__ import annotations

import httpx
import structlog

from app.config import settings
from app.integrations.base import AbstractSourceClient, RequestRaw, WagonRaw

log = structlog.get_logger(__name__)


class OneCClient(AbstractSourceClient):
    """HTTP-клиент для интеграции с 1С (HTTP-сервис или OData).

    Аутентификация — Basic Auth (``onec_login`` / ``onec_password``).
    Вагоны из 1С не забираются — метод возвращает пустой список.
    """

    def __init__(self) -> None:
        self._base_url = settings.onec_base_url
        self._auth = (settings.onec_login, settings.onec_password)

    async def fetch_wagons(self) -> list[WagonRaw]:
        # 1С не является источником вагонного парка
        return []

    async def fetch_requests(self) -> list[RequestRaw]:
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(
            base_url=self._base_url,
            auth=self._auth,
            timeout=timeout,
        ) as client:
            resp = await client.get("/requests", params={"status": "Новая"})
            resp.raise_for_status()
            data = resp.json()
            requests = [self._normalize_request(r) for r in data.get("value", [])]

        log.info("onec_client.fetch_requests.done", count=len(requests))
        return requests

    def _normalize_request(self, item: dict) -> RequestRaw:
        return RequestRaw(
            external_id_1c=str(item["Ref_Key"]),
            client_name=item.get("ClientName", ""),
            required_wagon_type=item.get("WagonType", ""),
            origin_station_code=item.get("OriginCode", ""),
            destination_station_code=item.get("DestCode", ""),
            planned_date=item.get("PlannedDate", ""),
            status=item.get("Status", "Новая"),
        )
