from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock

from etran_adapter.documents.registry import get_mapper, registered_types
from etran_adapter.schemas.gu12 import Gu12CargoItem, Gu12Request, Gu12WagonItem
from etran_adapter.schemas.redirection import RedirectionRequest
from etran_adapter.schemas.waybill import (
    WaybillCargo,
    WaybillParty,
    WaybillRequest,
    WaybillWagon,
)
from etran_adapter.status.codes import EtranDocumentStatus, resolve_status

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _make_settings():
    s = MagicMock()
    s.etran_login = "test_login"
    s.etran_password = MagicMock()
    s.etran_password.get_secret_value.return_value = "secret"
    s.etran_asu_go_id = "ASU001"
    return s


class TestEndToEndDocumentProcessing:
    """Сквозной тест: build_xml -> parse_xml через реестр маперов."""

    def test_gu12_roundtrip(self):
        mapper = get_mapper("GU12", _make_settings())
        request = Gu12Request(
            shipper_okpo="12345678",
            shipper_name="Тест",
            departure_station_code="20000",
            destination_station_code="30000",
            period_from=date(2026, 5, 1),
            period_to=date(2026, 5, 31),
            cargo_items=[
                Gu12CargoItem(
                    etsng_code="011001",
                    cargo_name="Уголь",
                    weight_kg=Decimal("60000"),
                )
            ],
            wagon_items=[
                Gu12WagonItem(wagon_type_code="90", wagon_count=1)
            ],
        )
        xml = mapper.build_xml(request)
        assert "<SendApplication>" in xml
        assert "<ShipperOKPO>12345678</ShipperOKPO>" in xml

        response_xml = (FIXTURES / "gu12_response.xml").read_text(encoding="utf-8")
        resp = mapper.parse_xml(response_xml)
        assert resp.request_id == "APP-2026-00123"

        status = resolve_status(resp.status_code)
        assert status == EtranDocumentStatus.GU12_UNDER_REVIEW

    def test_waybill_roundtrip(self):
        mapper = get_mapper("WAYBILL", _make_settings())
        request = WaybillRequest(
            operation_type="visaRequest",
            shipper=WaybillParty(
                okpo="12345678",
                name="Тест",
                station_code="20000",
                station_name="Ст. отпр.",
            ),
            consignee=WaybillParty(
                okpo="87654321",
                name="Получатель",
                station_code="30000",
                station_name="Ст. назн.",
            ),
            cargo=WaybillCargo(
                etsng_code="011001",
                cargo_name="Уголь",
                weight_gross_kg=Decimal("60000"),
            ),
            wagons=[WaybillWagon(wagon_number="12345678", wagon_type="ПВ")],
        )
        xml = mapper.build_xml(request)
        assert "<SendWaybill>" in xml

        response_xml = (FIXTURES / "waybill_response.xml").read_text(encoding="utf-8")
        resp = mapper.parse_xml(response_xml)
        assert resp.waybill_id == "WB-2026-00567"

        status = resolve_status(resp.status_code)
        assert status == EtranDocumentStatus.WAYBILL_VISA_PENDING

    def test_redirection_roundtrip(self):
        mapper = get_mapper("REDIRECTION", _make_settings())
        request = RedirectionRequest(
            waybill_id="WB-001",
            wagon_number="12345678",
            new_destination_station_code="40000",
            new_destination_station_name="Новая ст.",
            reason_code="01",
        )
        xml = mapper.build_xml(request)
        assert "<SendRedirection>" in xml

        response_xml = (FIXTURES / "redirection_response.xml").read_text(
            encoding="utf-8"
        )
        resp = mapper.parse_xml(response_xml)
        assert resp.redirection_id == "RD-2026-00089"

        status = resolve_status(resp.status_code)
        assert status == EtranDocumentStatus.REDIR_PENDING

    def test_all_document_types_registered(self):
        types = registered_types()
        assert types == ["GU12", "REDIRECTION", "WAYBILL"]
