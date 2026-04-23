from __future__ import annotations

from etran_adapter.schemas.redirection import RedirectionResponse
from etran_adapter.soap.xml_parser import extract_text, parse_response


def parse_redirection_response(xml_text: str) -> RedirectionResponse:
    """Разбор XML ответа ЭТРАН на запрос переадресовки."""
    root = parse_response(xml_text)
    redir = root.find(".//Redirection")
    if redir is None:
        redir = root

    approved_text = redir.findtext("Approved")
    approved: bool | None = None
    if approved_text is not None:
        approved = approved_text.lower() in ("true", "1", "yes")

    return RedirectionResponse(
        redirection_id=extract_text(redir, "RedirectionID"),
        status_code=extract_text(redir, "StatusCode"),
        status_description=extract_text(redir, "StatusDescription"),
        approved=approved,
        error_code=redir.findtext("ErrorCode"),
        error_message=redir.findtext("ErrorMessage"),
        raw_xml=xml_text,
    )
