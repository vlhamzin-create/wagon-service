from __future__ import annotations

from typing import Optional

import httpx
import structlog

from app.nsi_loader.config import NsiLoaderConfig

log = structlog.get_logger(__name__)


class NsiClient:
    """Фасад для запросов НСИ-справочников через etran-adapter."""

    def __init__(self, config: NsiLoaderConfig) -> None:
        self._base_url = config.etran_adapter_url
        self._api_key = config.etran_adapter_api_key
        self._timeout = config.etran_adapter_timeout

    async def fetch_nsi(
        self,
        nsi_type: str,
        chg_date_time: Optional[str] = None,
    ) -> str:
        """Запрашивает НСИ-справочник через etran-adapter и возвращает XML-ответ.

        Args:
            nsi_type: Тип справочника (StationList, WagonNSI, CargoList).
            chg_date_time: Метка для инкрементальной загрузки (ISO datetime).
        """
        params: dict[str, str] = {"NsiType": nsi_type}
        if chg_date_time:
            params["ChgDateTime"] = chg_date_time

        timeout = httpx.Timeout(self._timeout, connect=10.0)
        headers = {"X-Api-Key": self._api_key} if self._api_key else {}

        async with httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=timeout,
        ) as client:
            resp = await client.post("/api/v1/nsi", json=params)
            resp.raise_for_status()
            data = resp.json()

        xml_text: str = data["xml"]
        log.info(
            "nsi_client.fetch_done",
            nsi_type=nsi_type,
            incremental=chg_date_time is not None,
            response_len=len(xml_text),
        )
        return xml_text
