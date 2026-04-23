from __future__ import annotations

from typing import TYPE_CHECKING

from etran_adapter.schemas.redirection import RedirectionRequest, RedirectionResponse
from etran_adapter.xml.redirection_builder import build_redirection_xml
from etran_adapter.xml.redirection_parser import parse_redirection_response

if TYPE_CHECKING:
    from etran_adapter.config import Settings


class RedirectionMapper:
    """Маппер переадресовки: Pydantic-модель <-> XML ЭТРАН."""

    doc_type = "REDIRECTION"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_xml(self, request: RedirectionRequest) -> str:
        return build_redirection_xml(request, self._settings)

    def parse_xml(self, xml_text: str) -> RedirectionResponse:
        return parse_redirection_response(xml_text)
