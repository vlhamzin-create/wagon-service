from __future__ import annotations

from lxml import etree

from etran_adapter.soap.exceptions import EtranProtocolError, EtranSoapFaultError

NS_SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_XSD = "http://www.w3.org/2001/XMLSchema"
NS_ETRAN = "http://service.etran.rzd/"

SOAP_ENV = f"{{{NS_SOAP_ENV}}}"

SOAP_ACTION_GET_BLOCK = f"{NS_ETRAN}GetBlock"
SOAP_ACTION_SEND_BLOCK = f"{NS_ETRAN}SendBlock"


def build_envelope(method_name: str, text_payload: str) -> bytes:
    """Строит SOAP 1.1 конверт для GetBlock или SendBlock.

    ``text_payload`` — уже сериализованная XML-строка (или base64-строка),
    которая вставляется как текстовое значение элемента ``<Text>``.

    Возвращает UTF-8 байты готового SOAP-сообщения.
    """
    nsmap = {
        "soapenv": NS_SOAP_ENV,
        "xsi": NS_XSI,
        "xsd": NS_XSD,
    }

    envelope = etree.Element(SOAP_ENV + "Envelope", nsmap=nsmap)
    etree.SubElement(envelope, SOAP_ENV + "Header")
    body = etree.SubElement(envelope, SOAP_ENV + "Body")

    method_el = etree.SubElement(body, f"{{{NS_ETRAN}}}{method_name}")

    text_el = etree.SubElement(method_el, "Text")
    text_el.text = text_payload

    return etree.tostring(envelope, xml_declaration=True, encoding="UTF-8", pretty_print=False)


def parse_envelope_response(raw_bytes: bytes) -> str:
    """Парсит SOAP-ответ, проверяет Fault, возвращает текст элемента Text.

    Raises:
        EtranSoapFaultError: при наличии SOAP Fault.
        EtranProtocolError: при невалидном XML или отсутствии ожидаемых элементов.
    """
    try:
        root = etree.fromstring(raw_bytes)  # noqa: S320
    except etree.XMLSyntaxError as e:
        raise EtranProtocolError(f"Invalid XML in SOAP response: {e}") from e

    body_els = root.findall(SOAP_ENV + "Body")
    if not body_els:
        raise EtranProtocolError("SOAP response missing Body element")
    body = body_els[0]

    fault_el = body.find(SOAP_ENV + "Fault")
    if fault_el is not None:
        fault_code = _text(fault_el, "faultcode")
        fault_string = _text(fault_el, "faultstring")
        detail_el = fault_el.find("detail")
        detail_text = (
            etree.tostring(detail_el, encoding="unicode") if detail_el is not None else None
        )
        raise EtranSoapFaultError(fault_code, fault_string, detail_text)

    # Извлекаем Text из ответа метода (первый дочерний элемент Body)
    method_response = body[0] if len(body) > 0 else None
    if method_response is None:
        raise EtranProtocolError("SOAP Body has no method response element")

    text_el = method_response.find("Text")
    if text_el is None:
        # Пробуем с namespace
        text_el = method_response.find(f"{{{NS_ETRAN}}}Text")

    if text_el is not None and text_el.text:
        return text_el.text

    # Если нет Text, возвращаем сериализованное содержимое метода
    return etree.tostring(method_response, encoding="unicode")


def _text(parent: etree._Element, tag: str) -> str:
    el = parent.find(tag)
    return el.text.strip() if el is not None and el.text else ""
