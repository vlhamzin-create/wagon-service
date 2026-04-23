from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from lxml import etree

from etran_adapter.documents.redirection import RedirectionMapper
from etran_adapter.schemas.redirection import RedirectionRequest

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def _make_settings():
    s = MagicMock()
    s.etran_login = "test_login"
    s.etran_password = MagicMock()
    s.etran_password.get_secret_value.return_value = "secret"
    s.etran_asu_go_id = "ASU001"
    return s


def _make_request() -> RedirectionRequest:
    return RedirectionRequest(
        waybill_id="WB-2026-00567",
        wagon_number="12345678",
        new_destination_station_code="40000",
        new_destination_station_name="Новая станция",
        reason_code="01",
        reason_description="Изменение маршрута",
    )


class TestRedirectionMapperBuildXml:
    def test_produces_valid_xml(self):
        mapper = RedirectionMapper(_make_settings())
        xml_str = mapper.build_xml(_make_request())
        root = etree.fromstring(xml_str.encode("utf-8"))

        assert root.tag == "SendRedirection"
        redir = root.find("Redirection")
        assert redir is not None
        assert redir.findtext("WaybillID") == "WB-2026-00567"
        assert redir.findtext("WagonNumber") == "12345678"
        assert redir.findtext("NewDestStationCode") == "40000"
        assert redir.findtext("ReasonCode") == "01"

    def test_optional_fields_omitted(self):
        request = RedirectionRequest(
            waybill_id="WB-001",
            wagon_number="11111111",
            new_destination_station_code="50000",
            new_destination_station_name="Другая станция",
            reason_code="02",
        )
        mapper = RedirectionMapper(_make_settings())
        xml_str = mapper.build_xml(request)
        root = etree.fromstring(xml_str.encode("utf-8"))

        redir = root.find("Redirection")
        assert redir.find("NewConsigneeOKPO") is None
        assert redir.find("ReasonDescription") is None


class TestRedirectionMapperParseXml:
    def test_parses_success_response(self):
        xml_text = (FIXTURES / "redirection_response.xml").read_text(encoding="utf-8")
        mapper = RedirectionMapper(_make_settings())
        resp = mapper.parse_xml(xml_text)

        assert resp.redirection_id == "RD-2026-00089"
        assert resp.status_code == "20"
        assert resp.status_description == "Ожидает одобрения"
        assert resp.approved is False
        assert resp.raw_xml == xml_text

    def test_approved_true(self):
        xml_text = (
            "<Response><Redirection>"
            "<RedirectionID>RD-001</RedirectionID>"
            "<StatusCode>21</StatusCode>"
            "<StatusDescription>Одобрена</StatusDescription>"
            "<Approved>true</Approved>"
            "</Redirection></Response>"
        )
        mapper = RedirectionMapper(_make_settings())
        resp = mapper.parse_xml(xml_text)
        assert resp.approved is True

    def test_approved_none_when_absent(self):
        xml_text = (
            "<Response><Redirection>"
            "<RedirectionID>RD-002</RedirectionID>"
            "<StatusCode>20</StatusCode>"
            "<StatusDescription>Ожидает</StatusDescription>"
            "</Redirection></Response>"
        )
        mapper = RedirectionMapper(_make_settings())
        resp = mapper.parse_xml(xml_text)
        assert resp.approved is None
