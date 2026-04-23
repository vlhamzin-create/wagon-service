from __future__ import annotations

from typing import Any

from lxml import etree

from etran_adapter.config import settings
from etran_adapter.operations.base import BaseOperation
from etran_adapter.soap.xml_builder import wrap_request


class RedirectionOperation(BaseOperation):
    """Операции переадресовки (раздел 5.11.x спецификации)."""

    def build_xml(self, params: dict[str, Any]) -> str:
        body = etree.Element("Redirection")
        for key, value in params.items():
            etree.SubElement(body, key).text = str(value)
        return wrap_request("SendRedirection", settings, body)
