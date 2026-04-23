from __future__ import annotations

from typing import TYPE_CHECKING

from etran_adapter.schemas.waybill import WaybillRequest, WaybillResponse
from etran_adapter.xml.waybill_builder import build_waybill_xml
from etran_adapter.xml.waybill_parser import parse_waybill_response

if TYPE_CHECKING:
    from etran_adapter.config import Settings


class WaybillMapper:
    """Маппер накладной: Pydantic-модель <-> XML ЭТРАН."""

    doc_type = "WAYBILL"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_xml(self, request: WaybillRequest) -> str:
        return build_waybill_xml(request, self._settings)

    def parse_xml(self, xml_text: str) -> WaybillResponse:
        return parse_waybill_response(xml_text)
