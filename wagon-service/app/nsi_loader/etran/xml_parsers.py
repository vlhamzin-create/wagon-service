from __future__ import annotations

from lxml import etree

from app.nsi_loader.models.cargo import CargoRecord
from app.nsi_loader.models.station import StationRecord
from app.nsi_loader.models.wagon_type import WagonTypeRecord


def _text(el: etree._Element, tag: str) -> str | None:
    """Извлекает текст дочернего элемента или None."""
    child = el.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return None


def _int(el: etree._Element, tag: str) -> int | None:
    val = _text(el, tag)
    return int(val) if val else None


def _float(el: etree._Element, tag: str) -> float | None:
    val = _text(el, tag)
    return float(val) if val else None


def _bool(el: etree._Element, tag: str, default: bool = False) -> bool:
    val = _text(el, tag)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes")


def parse_stations(xml_text: str) -> list[StationRecord]:
    """Парсит XML-ответ справочника станций в список StationRecord."""
    root = etree.fromstring(xml_text.encode("utf-8"))  # noqa: S320
    records: list[StationRecord] = []
    for station_el in root.iter("Station"):
        code = _text(station_el, "Code")
        name = _text(station_el, "Name")
        if not code or not name:
            continue
        records.append(
            StationRecord(
                code=code,
                name=name,
                short_name=_text(station_el, "ShortName"),
                country_code=_text(station_el, "CountryCode"),
                country_name=_text(station_el, "CountryName"),
                railway_code=_text(station_el, "RailwayCode"),
                railway_name=_text(station_el, "RailwayName"),
                is_active=_bool(station_el, "IsActive", default=True),
                etran_version=_int(station_el, "Version"),
            )
        )
    return records


def parse_wagon_types(xml_text: str) -> list[WagonTypeRecord]:
    """Парсит XML-ответ НСИ вагонов в список WagonTypeRecord."""
    root = etree.fromstring(xml_text.encode("utf-8"))  # noqa: S320
    records: list[WagonTypeRecord] = []
    for wagon_el in root.iter("WagonType"):
        type_code = _text(wagon_el, "TypeCode")
        type_name = _text(wagon_el, "TypeName")
        if not type_code or not type_name:
            continue
        records.append(
            WagonTypeRecord(
                type_code=type_code,
                type_name=type_name,
                cargo_capacity=_float(wagon_el, "CargoCapacity"),
                volume=_float(wagon_el, "Volume"),
                tare_weight=_float(wagon_el, "TareWeight"),
                axle_count=_int(wagon_el, "AxleCount"),
                is_active=_bool(wagon_el, "IsActive", default=True),
                etran_version=_int(wagon_el, "Version"),
            )
        )
    return records


def parse_cargos(xml_text: str) -> list[CargoRecord]:
    """Парсит XML-ответ справочника грузов в список CargoRecord."""
    root = etree.fromstring(xml_text.encode("utf-8"))  # noqa: S320
    records: list[CargoRecord] = []
    for cargo_el in root.iter("Cargo"):
        etsng_code = _text(cargo_el, "EtsngCode")
        etsng_name = _text(cargo_el, "EtsngName")
        if not etsng_code or not etsng_name:
            continue
        records.append(
            CargoRecord(
                etsng_code=etsng_code,
                etsng_name=etsng_name,
                gng_code=_text(cargo_el, "GngCode"),
                gng_name=_text(cargo_el, "GngName"),
                cargo_group=_text(cargo_el, "CargoGroup"),
                is_dangerous=_bool(cargo_el, "IsDangerous"),
                is_active=_bool(cargo_el, "IsActive", default=True),
                etran_version=_int(cargo_el, "Version"),
            )
        )
    return records
