from __future__ import annotations

from typing import Any

from lxml import etree

from etran_adapter.config import settings
from etran_adapter.operations.base import BaseOperation
from etran_adapter.soap.xml_builder import wrap_request


class ApplicationOperation(BaseOperation):
    """Операции с заявками ГУ-12 (раздел 5.2.x спецификации)."""

    def build_xml(self, params: dict[str, Any]) -> str:
        body = etree.Element("Application")
        for key, value in params.items():
            etree.SubElement(body, key).text = str(value)
        return wrap_request("SendApplication", settings, body)
