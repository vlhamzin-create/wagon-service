from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

from lxml import etree

from etran_adapter.documents.waybill import WaybillMapper
from etran_adapter.schemas.waybill import (
    WaybillCargo,
    WaybillParty,
    WaybillRequest,
    WaybillWagon,
)

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _make_settings():
    s = MagicMock()
    s.etran_login = "test_login"
    s.etran_password = MagicMock()
    s.etran_password.get_secret_value.return_value = "secret"
    s.etran_asu_go_id = "ASU001"
    return s


def _make_request() -> WaybillRequest:
    return WaybillRequest(
        operation_type="visaRequest",
        shipper=WaybillParty(
            okpo="12345678",
            name="ООО Грузоотправитель",
            station_code="20000",
            station_name="Станция отправления",
        ),
        consignee=WaybillParty(
            okpo="87654321",
            name="ООО Грузополучатель",
            station_code="30000",
            station_name="Станция назначения",
        ),
        cargo=WaybillCargo(
            etsng_code="011001",
            cargo_name="Уголь каменный",
            weight_gross_kg=Decimal("60000"),
        ),
        wagons=[
            WaybillWagon(wagon_number="12345678", wagon_type="Полувагон"),
        ],
    )


class TestWaybillMapperBuildXml:
    def test_produces_valid_xml(self):
        mapper = WaybillMapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        assert root.tag == "SendWaybill"
        wb = root.find("Waybill")
        assert wb is not None
        assert wb.findtext("OperationType") == "visaRequest"

    def test_shipper_consignee_present(self):
        mapper = WaybillMapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        assert root.findtext(".//Shipper/OKPO") == "12345678"
        assert root.findtext(".//Consignee/OKPO") == "87654321"
        assert root.findtext(".//Consignee/StationName") == "Станция назначения"

    def test_wagon_list_present(self):
        mapper = WaybillMapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        wagon = root.find(".//WagonList/Wagon")
        assert wagon is not None
        assert wagon.findtext("WagonNumber") == "12345678"
        assert wagon.findtext("WagonType") == "Полувагон"


class TestWaybillMapperParseXml:
    def test_parses_success_response(self):
        xml_text = (FIXTURES / "waybill_response.xml").read_text(encoding="utf-8")
        mapper = WaybillMapper(_make_settings())
        resp = mapper.parse_xml(xml_text)

        assert resp.waybill_id == "WB-2026-00567"
        assert resp.waybill_number == "ЭК-0001234"
        assert resp.visa_status == "Pending"
        assert resp.status_code == "10"
        assert resp.status_description == "Ожидает визы"
        assert resp.raw_xml == xml_text
