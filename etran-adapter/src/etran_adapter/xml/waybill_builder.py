from __future__ import annotations

from lxml import etree

from etran_adapter.config import Settings
from etran_adapter.schemas.waybill import WaybillParty, WaybillRequest
from etran_adapter.soap.xml_builder import wrap_request


def _add_party(parent: etree._Element, tag: str, party: WaybillParty) -> None:
    el = etree.SubElement(parent, tag)
    etree.SubElement(el, "OKPO").text = party.okpo
    etree.SubElement(el, "Name").text = party.name
    if party.inn:
        etree.SubElement(el, "INN").text = party.inn
    etree.SubElement(el, "StationCode").text = party.station_code
    etree.SubElement(el, "StationName").text = party.station_name


def build_waybill_xml(request: WaybillRequest, settings: Settings) -> str:
    """Сборка XML запроса накладной для параметра Text."""
    body = etree.Element("Waybill")
    etree.SubElement(body, "OperationType").text = request.operation_type

    _add_party(body, "Shipper", request.shipper)
    _add_party(body, "Consignee", request.consignee)

    cargo_el = etree.SubElement(body, "Cargo")
    etree.SubElement(cargo_el, "EtsngCode").text = request.cargo.etsng_code
    etree.SubElement(cargo_el, "CargoName").text = request.cargo.cargo_name
    etree.SubElement(cargo_el, "WeightGrossKg").text = str(request.cargo.weight_gross_kg)
    if request.cargo.weight_tare_kg is not None:
        etree.SubElement(cargo_el, "WeightTareKg").text = str(request.cargo.weight_tare_kg)
    if request.cargo.package_type_code:
        etree.SubElement(cargo_el, "PackageTypeCode").text = request.cargo.package_type_code
    if request.cargo.package_count is not None:
        etree.SubElement(cargo_el, "PackageCount").text = str(request.cargo.package_count)

    wagon_list = etree.SubElement(body, "WagonList")
    for w in request.wagons:
        wagon_el = etree.SubElement(wagon_list, "Wagon")
        etree.SubElement(wagon_el, "WagonNumber").text = w.wagon_number
        etree.SubElement(wagon_el, "WagonType").text = w.wagon_type
        if w.load_capacity_t is not None:
            etree.SubElement(wagon_el, "LoadCapacityT").text = str(w.load_capacity_t)
        if w.tare_weight_t is not None:
            etree.SubElement(wagon_el, "TareWeightT").text = str(w.tare_weight_t)

    if request.departure_date:
        etree.SubElement(body, "DepartureDate").text = request.departure_date.isoformat()
    if request.gu12_id:
        etree.SubElement(body, "Gu12ID").text = request.gu12_id
    if request.special_marks:
        etree.SubElement(body, "SpecialMarks").text = request.special_marks

    return wrap_request("SendWaybill", settings, body)
