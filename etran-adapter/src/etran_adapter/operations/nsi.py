from __future__ import annotations

from typing import Any

from etran_adapter.config import Settings, settings
from etran_adapter.operations.base import BaseOperation
from etran_adapter.soap.xml_builder import wrap_request


class NsiOperation(BaseOperation):
    """Операции справочников НСИ (раздел 5.5.x спецификации)."""

    def build_xml(self, params: dict[str, Any]) -> str:
        from lxml import etree

        body = etree.Element("Filter")
        for key, value in params.items():
            etree.SubElement(body, key).text = str(value)
        return wrap_request("GetNSI", settings, body)

    @staticmethod
    def build_ping_xml(s: Settings) -> str:
        """Лёгкий запрос НСИ для health-check."""
        return wrap_request("GetNSI", s, None)
