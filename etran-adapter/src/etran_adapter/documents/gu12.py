from __future__ import annotations

from typing import TYPE_CHECKING

from etran_adapter.schemas.gu12 import Gu12Request, Gu12Response
from etran_adapter.xml.gu12_builder import build_gu12_xml
from etran_adapter.xml.gu12_parser import parse_gu12_response

if TYPE_CHECKING:
    from etran_adapter.config import Settings


class Gu12Mapper:
    """Маппер заявки ГУ-12: Pydantic-модель <-> XML ЭТРАН."""

    doc_type = "GU12"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_xml(self, request: Gu12Request) -> str:
        return build_gu12_xml(request, self._settings)

    def parse_xml(self, xml_text: str) -> Gu12Response:
        return parse_gu12_response(xml_text)
