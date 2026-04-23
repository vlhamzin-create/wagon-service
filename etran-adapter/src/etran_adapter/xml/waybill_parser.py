from __future__ import annotations

from etran_adapter.schemas.waybill import WaybillResponse
from etran_adapter.soap.xml_parser import extract_text, parse_response


def parse_waybill_response(xml_text: str) -> WaybillResponse:
    """Разбор XML ответа ЭТРАН на запрос по накладной."""
    root = parse_response(xml_text)
    wb = root.find(".//Waybill")
    if wb is None:
        wb = root

    return WaybillResponse(
        waybill_id=extract_text(wb, "WaybillID"),
        waybill_number=wb.findtext("Number"),
        visa_status=wb.findtext("VisaStatus"),
        status_code=extract_text(wb, "StatusCode", default=extract_text(wb, "Status")),
        status_description=extract_text(wb, "StatusDescription"),
        error_code=wb.findtext("ErrorCode"),
        error_message=wb.findtext("ErrorMessage"),
        raw_xml=xml_text,
    )
