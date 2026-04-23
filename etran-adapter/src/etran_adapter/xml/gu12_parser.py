from __future__ import annotations

from etran_adapter.schemas.gu12 import Gu12Response
from etran_adapter.soap.xml_parser import extract_text, parse_response


def parse_gu12_response(xml_text: str) -> Gu12Response:
    """Разбор XML ответа ЭТРАН на запрос ГУ-12."""
    root = parse_response(xml_text)
    app = root.find(".//Application")
    if app is None:
        app = root

    return Gu12Response(
        request_id=extract_text(app, "RequestID"),
        etran_doc_number=app.findtext("DocNumber"),
        status_code=extract_text(app, "StatusCode"),
        status_description=extract_text(app, "StatusDescription"),
        error_code=app.findtext("ErrorCode"),
        error_message=app.findtext("ErrorMessage"),
        raw_xml=xml_text,
    )
