from __future__ import annotations

from typing import Protocol, TypeVar

RequestModel = TypeVar("RequestModel")
ResponseModel = TypeVar("ResponseModel")


class DocumentMapper(Protocol[RequestModel, ResponseModel]):
    """Протокол маппера документа ЭТРАН.

    build_xml — превращает доменную модель в XML-строку для параметра Text.
    parse_xml — разбирает XML из параметра Text ответа в доменную модель.
    """

    doc_type: str

    def build_xml(self, request: RequestModel) -> str: ...

    def parse_xml(self, xml_text: str) -> ResponseModel: ...
