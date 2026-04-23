from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

from app.config import settings
from app.integrations.base import AbstractSourceClient, RequestRaw, WagonRaw
from app.integrations.exceptions import (
    OneCServerError,
    OneCUnavailableError,
    OneCValidationError,
)

log = structlog.get_logger(__name__)


@dataclass
class OneCAssignmentPayload:
    """Payload для передачи одного назначения в 1С."""

    idempotency_key: str
    wagon_ids: list[str]
    station_code: str | None
    client_external_id: str | None
    comment: str | None
    assigned_at: str  # ISO 8601
    assigned_by_user_id: str


@dataclass
class OneCAssignmentResponse:
    success: bool
    onec_document_id: str | None
    message: str
    status_code: int


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

    # ------------------------------------------------------------------
    # Отправка назначения в 1С
    # ------------------------------------------------------------------

    async def send_assignment(
        self, payload: OneCAssignmentPayload
    ) -> OneCAssignmentResponse:
        url = settings.onec_assignment_url or f"{self._base_url}/assignments"
        timeout = httpx.Timeout(settings.onec_assignment_timeout, connect=5.0)
        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": payload.idempotency_key,
        }
        body = {
            "idempotencyKey": payload.idempotency_key,
            "wagons": payload.wagon_ids,
            "destinationStationCode": payload.station_code,
            "clientId": payload.client_external_id,
            "comment": payload.comment,
            "assignedAt": payload.assigned_at,
            "assignedByUserId": payload.assigned_by_user_id,
        }

        bound = log.bind(
            idempotency_key=payload.idempotency_key,
            wagon_count=len(payload.wagon_ids),
        )
        bound.info("onec.send_assignment.start")

        try:
            async with httpx.AsyncClient(
                auth=self._auth, timeout=timeout
            ) as client:
                resp = await client.post(url, json=body, headers=headers)
        except (httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout) as exc:
            bound.warning("onec.send_assignment.unavailable", error=str(exc))
            raise OneCUnavailableError(f"1С недоступна: {exc}") from exc

        bound = bound.bind(status_code=resp.status_code)

        if resp.status_code == 200:
            data = resp.json()
            bound.info(
                "onec.send_assignment.success",
                onec_doc_id=data.get("documentId"),
            )
            return OneCAssignmentResponse(
                success=True,
                onec_document_id=data.get("documentId"),
                message="OK",
                status_code=resp.status_code,
            )

        if 400 <= resp.status_code < 500:
            bound.warning(
                "onec.send_assignment.validation_error",
                body=resp.text[:500],
            )
            raise OneCValidationError(
                f"Ошибка валидации 1С: HTTP {resp.status_code}",
                response_body=resp.text,
            )

        bound.error("onec.send_assignment.server_error", body=resp.text[:500])
        raise OneCServerError(
            f"Ошибка сервера 1С: HTTP {resp.status_code}",
            status_code=resp.status_code,
            response_body=resp.text,
        )
