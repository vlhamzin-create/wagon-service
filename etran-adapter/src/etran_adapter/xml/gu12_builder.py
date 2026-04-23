from __future__ import annotations

from lxml import etree

from etran_adapter.config import Settings
from etran_adapter.schemas.gu12 import Gu12Request
from etran_adapter.soap.xml_builder import wrap_request


def build_gu12_xml(request: Gu12Request, settings: Settings) -> str:
    """Сборка XML запроса заявки ГУ-12 для параметра Text."""
    body = etree.Element("Application")

    etree.SubElement(body, "ShipperOKPO").text = request.shipper_okpo
    etree.SubElement(body, "ShipperName").text = request.shipper_name
    etree.SubElement(body, "DepartureStationCode").text = request.departure_station_code
    etree.SubElement(body, "DestinationStationCode").text = request.destination_station_code
    etree.SubElement(body, "PeriodFrom").text = request.period_from.isoformat()
    etree.SubElement(body, "PeriodTo").text = request.period_to.isoformat()

    if request.payer_okpo:
        etree.SubElement(body, "PayerOKPO").text = request.payer_okpo
    if request.special_conditions:
        etree.SubElement(body, "SpecialConditions").text = request.special_conditions

    cargo_list = etree.SubElement(body, "CargoList")
    for item in request.cargo_items:
        cargo_el = etree.SubElement(cargo_list, "Cargo")
        etree.SubElement(cargo_el, "EtsngCode").text = item.etsng_code
        etree.SubElement(cargo_el, "CargoName").text = item.cargo_name
        etree.SubElement(cargo_el, "WeightKg").text = str(item.weight_kg)
        if item.container_count is not None:
            etree.SubElement(cargo_el, "ContainerCount").text = str(item.container_count)

    wagon_list = etree.SubElement(body, "WagonList")
    for item in request.wagon_items:
        wagon_el = etree.SubElement(wagon_list, "Wagon")
        etree.SubElement(wagon_el, "WagonTypeCode").text = item.wagon_type_code
        etree.SubElement(wagon_el, "WagonCount").text = str(item.wagon_count)
        if item.wagon_numbers:
            numbers_el = etree.SubElement(wagon_el, "WagonNumbers")
            for num in item.wagon_numbers:
                etree.SubElement(numbers_el, "Number").text = num

    return wrap_request("SendApplication", settings, body)
