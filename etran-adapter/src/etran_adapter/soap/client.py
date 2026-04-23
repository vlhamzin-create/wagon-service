from __future__ import annotations

import structlog

from etran_adapter.config import Settings
from etran_adapter.soap.base64_helper import decode_text, is_base64
from etran_adapter.soap.envelope import (
    SOAP_ACTION_GET_BLOCK,
    SOAP_ACTION_SEND_BLOCK,
    build_envelope,
    parse_envelope_response,
)
from etran_adapter.soap.transport import HttpTransport

logger = structlog.get_logger(__name__)


class EtranSoapClient:
    """SOAP 1.1 клиент для вызовов GetBlock/SendBlock АС ЭТРАН.

    Использует ручную сборку SOAP-конвертов (lxml) и httpx-транспорт.
    Zeep не используется, так как параметр ``Text`` содержит вложенный XML
    в виде строки, и Zeep экранирует его, ломая структуру.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._transport = HttpTransport(settings)

    def send_block(self, xml_text: str) -> str:
        """Вызов SendBlock. Возвращает ``Text`` из ответа."""
        return self._call("SendBlock", SOAP_ACTION_SEND_BLOCK, xml_text)

    def get_block(self, xml_text: str) -> str:
        """Вызов GetBlock. Возвращает ``Text`` из ответа."""
        return self._call("GetBlock", SOAP_ACTION_GET_BLOCK, xml_text)

    def _call(self, method: str, soap_action: str, xml_text: str) -> str:
        logger.info("etran_soap_call", method=method)

        envelope_bytes = build_envelope(method, xml_text)
        raw_response = self._transport.post_soap(soap_action, envelope_bytes)
        text_response = parse_envelope_response(raw_response)

        # Автоматически декодируем base64, если ответ закодирован
        if is_base64(text_response):
            logger.debug("etran_soap_response.base64_detected", method=method)
            text_response = decode_text(text_response)

        return text_response

    def ping(self) -> bool:
        """Проверка соединения через лёгкий НСИ-запрос (health-check)."""
        from etran_adapter.operations.nsi import NsiOperation

        xml = NsiOperation.build_ping_xml(self._settings)
        try:
            resp = self.get_block(xml)
            return "<Error>" not in resp
        except Exception:
            logger.warning("etran_ping.failed", exc_info=True)
            return False

    def close(self) -> None:
        """Освобождает HTTP-соединения."""
        self._transport.close()
