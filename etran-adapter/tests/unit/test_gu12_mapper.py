from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from lxml import etree

from etran_adapter.documents.gu12 import Gu12Mapper
from etran_adapter.schemas.gu12 import (
    Gu12CargoItem,
    Gu12Request,
    Gu12WagonItem,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _make_settings():
    s = MagicMock()
    s.etran_login = "test_login"
    s.etran_password = MagicMock()
    s.etran_password.get_secret_value.return_value = "secret"
    s.etran_asu_go_id = "ASU001"
    return s


def _make_request() -> Gu12Request:
    return Gu12Request(
        shipper_okpo="12345678",
        shipper_name="ООО Грузоотправитель",
        departure_station_code="20000",
        destination_station_code="30000",
        period_from=date(2026, 5, 1),
        period_to=date(2026, 5, 31),
        cargo_items=[
            Gu12CargoItem(
                etsng_code="011001",
                cargo_name="Уголь каменный",
                weight_kg=Decimal("60000"),
            )
        ],
        wagon_items=[
            Gu12WagonItem(
                wagon_type_code="90",
                wagon_count=2,
                wagon_numbers=["12345678", "87654321"],
            )
        ],
    )


class TestGu12MapperBuildXml:
    def test_produces_valid_xml(self):
        mapper = Gu12Mapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        assert root.tag == "SendApplication"
        assert root.find("AccessParams") is not None
        app = root.find("Application")
        assert app is not None
        assert app.findtext("ShipperOKPO") == "12345678"
        assert app.findtext("DepartureStationCode") == "20000"

    def test_cargo_list_present(self):
        mapper = Gu12Mapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        cargo = root.find(".//CargoList/Cargo")
        assert cargo is not None
        assert cargo.findtext("EtsngCode") == "011001"
        assert cargo.findtext("WeightKg") == "60000"

    def test_wagon_numbers_present(self):
        mapper = Gu12Mapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        numbers = root.findall(".//WagonNumbers/Number")
        assert len(numbers) == 2
        assert numbers[0].text == "12345678"
        assert numbers[1].text == "87654321"


class TestGu12MapperParseXml:
    def test_parses_success_response(self):
        xml_text = (FIXTURES / "gu12_response.xml").read_text(encoding="utf-8")
        mapper = Gu12Mapper(_make_settings())
        resp = mapper.parse_xml(xml_text)

        assert resp.request_id == "APP-2026-00123"
        assert resp.etran_doc_number == "ГУ12-0001234"
        assert resp.status_code == "3"
        assert resp.status_description == "На согласовании"
        assert resp.error_code is None
        assert resp.raw_xml == xml_text

    def test_parses_error_response(self):
        xml_text = (
            "<Response>"
            "<Error><Code>VAL01</Code><Message>Ошибка валидации</Message></Error>"
            "</Response>"
        )
        from etran_adapter.soap.xml_parser import EtranResponseError

        mapper = Gu12Mapper(_make_settings())
        with pytest.raises(EtranResponseError) as exc_info:
            mapper.parse_xml(xml_text)
        assert exc_info.value.code == "VAL01"


class TestGu12Validation:
    def test_invalid_wagon_number_rejected(self):
        with pytest.raises(ValueError, match="Invalid wagon number"):
            Gu12WagonItem(
                wagon_type_code="90",
                wagon_count=1,
                wagon_numbers=["123"],
            )

    def test_valid_wagon_number_accepted(self):
        item = Gu12WagonItem(
            wagon_type_code="90",
            wagon_count=1,
            wagon_numbers=["12345678"],
        )
        assert item.wagon_numbers == ["12345678"]
