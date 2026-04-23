from __future__ import annotations

import structlog
import zeep

from etran_adapter.config import Settings
from etran_adapter.soap.transport import LoggingTransport

logger = structlog.get_logger(__name__)


class EtranSoapClient:
    """Тонкая обёртка вокруг zeep.Client для вызовов GetBlock/SendBlock.

    ЭТРАН передаёт бизнес-XML как строку в параметре ``Text``.
    Zeep используется только для формирования SOAP-конверта.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        transport = LoggingTransport(
            timeout=settings.etran_timeout_seconds,
            operation_timeout=settings.etran_timeout_seconds,
        )
        self._client = zeep.Client(
            wsdl=str(settings.etran_wsdl_url),
            transport=transport,
        )
        self._service = self._client.create_service(
            binding_name="{http://service.etran.rzd/}EtranServiceBinding",
            address=str(settings.etran_endpoint_url),
        )

    def send_block(self, xml_text: str) -> str:
        """Вызов SendBlock. Возвращает ``Text`` из ответа."""
        result = self._service.SendBlock(Text=xml_text)
        return result

    def get_block(self, xml_text: str) -> str:
        """Вызов GetBlock."""
        result = self._service.GetBlock(Text=xml_text)
        return result

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
