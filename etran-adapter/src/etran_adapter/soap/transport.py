from __future__ import annotations

import re

import structlog
from zeep.transports import Transport

logger = structlog.get_logger(__name__)

_PASSWORD_RE = re.compile(r"<Password>[^<]+</Password>")


class LoggingTransport(Transport):
    """Zeep Transport с логированием SOAP-конвертов и маскированием credentials."""

    def post(self, address, message, headers):
        logger.debug(
            "etran_soap_request",
            address=address,
            message_preview=self._mask_credentials(message[:500]),
        )
        response = super().post(address, message, headers)
        logger.debug(
            "etran_soap_response",
            status_code=response.status_code,
            response_preview=response.content[:500],
        )
        return response

    @staticmethod
    def _mask_credentials(text: str | bytes) -> str:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="replace")
        return _PASSWORD_RE.sub("<Password>***</Password>", text)
