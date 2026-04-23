from __future__ import annotations

from lxml import etree


class EtranResponseError(Exception):
    """Ошибка, извлечённая из XML-ответа ЭТРАН (тег <Error>)."""

    def __init__(self, code: str, message: str, raw_xml: str) -> None:
        super().__init__(f"ETRAN error {code}: {message}")
        self.code = code
        self.message = message
        self.raw_xml = raw_xml


def parse_response(xml_text: str) -> etree._Element:
    """Парсит Text-ответ ЭТРАН и проверяет наличие <Error>.

    Возвращает корневой элемент. Бросает ``EtranResponseError``
    если ответ содержит блок ошибки.
    """
    root = etree.fromstring(xml_text.encode("utf-8"))  # noqa: S320

    error_el = root.find(".//Error")
    if error_el is not None:
        code = error_el.findtext("Code", default="UNKNOWN")
        message = error_el.findtext("Message", default="")
        raise EtranResponseError(code=code, message=message, raw_xml=xml_text)

    return root


def extract_text(element: etree._Element, xpath: str, default: str = "") -> str:
    """Безопасное извлечение текста по XPath."""
    return element.findtext(xpath, default=default)
