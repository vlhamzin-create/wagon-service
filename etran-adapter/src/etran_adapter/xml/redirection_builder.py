from __future__ import annotations

from lxml import etree

from etran_adapter.config import Settings
from etran_adapter.schemas.redirection import RedirectionRequest
from etran_adapter.soap.xml_builder import wrap_request


def build_redirection_xml(request: RedirectionRequest, settings: Settings) -> str:
    """Сборка XML запроса переадресовки для параметра Text."""
    body = etree.Element("Redirection")

    etree.SubElement(body, "WaybillID").text = request.waybill_id
    etree.SubElement(body, "WagonNumber").text = request.wagon_number
    etree.SubElement(body, "NewDestStationCode").text = request.new_destination_station_code
    etree.SubElement(body, "NewDestStationName").text = request.new_destination_station_name

    if request.new_consignee_okpo:
        etree.SubElement(body, "NewConsigneeOKPO").text = request.new_consignee_okpo
    if request.new_consignee_name:
        etree.SubElement(body, "NewConsigneeName").text = request.new_consignee_name

    etree.SubElement(body, "ReasonCode").text = request.reason_code
    if request.reason_description:
        etree.SubElement(body, "ReasonDescription").text = request.reason_description

    return wrap_request("SendRedirection", settings, body)
