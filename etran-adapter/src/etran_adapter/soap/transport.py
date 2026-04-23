from __future__ import annotations

import re

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from etran_adapter.config import Settings
from etran_adapter.soap.exceptions import EtranTransportError

logger = structlog.get_logger(__name__)

_PASSWORD_RE = re.compile(r"<Password>[^<]+</Password>")


class HttpTransport:
    """Синхронный HTTP-транспорт поверх httpx.

    Управляет сессией, TLS, retry, таймаутами.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = self._build_client()

    def _build_client(self) -> httpx.Client:
        timeout = httpx.Timeout(
            connect=float(self._settings.etran_timeout_seconds),
            read=float(self._settings.etran_timeout_seconds),
            write=30.0,
            pool=5.0,
        )
        return httpx.Client(timeout=timeout)

    def post_soap(self, soap_action: str, body_bytes: bytes) -> bytes:
        """Отправляет SOAP-запрос, возвращает тело ответа.

        Retry на сетевые ошибки и HTTP 5xx (кроме 500 с SOAP Fault).
        """
        return self._post_with_retry(soap_action, body_bytes)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.5, min=1, max=10),
        retry=retry_if_exception_type(EtranTransportError),
        reraise=True,
    )
    def _post_with_retry(self, soap_action: str, body_bytes: bytes) -> bytes:
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": soap_action,
        }

        logger.debug(
            "etran_soap_request",
            address=str(self._settings.etran_endpoint_url),
            message_preview=self._mask_credentials(body_bytes[:500]),
        )

        try:
            response = self._client.post(
                str(self._settings.etran_endpoint_url),
                content=body_bytes,
                headers=headers,
            )
        except httpx.TimeoutException as e:
            raise EtranTransportError(f"Request timeout: {e}", cause=e) from e
        except httpx.TransportError as e:
            raise EtranTransportError(f"Transport error: {e}", cause=e) from e

        logger.debug(
            "etran_soap_response",
            status_code=response.status_code,
            response_preview=response.content[:500],
        )

        # HTTP 500 с телом — может быть SOAP Fault, не ретраим
        if response.status_code == 500:
            return response.content

        # Другие 5xx — ретраим
        if response.status_code >= 500:
            raise EtranTransportError(
                f"Server error HTTP {response.status_code}",
                status_code=response.status_code,
            )

        if response.status_code >= 400:
            raise EtranTransportError(
                f"Client error HTTP {response.status_code}",
                status_code=response.status_code,
            )

        return response.content

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def _mask_credentials(text: str | bytes) -> str:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        return _PASSWORD_RE.sub("<Password>***</Password>", text)
