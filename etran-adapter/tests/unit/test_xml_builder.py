from __future__ import annotations

from unittest.mock import MagicMock

from lxml import etree

from etran_adapter.soap.xml_builder import build_access_params, wrap_request


def _make_settings(**overrides):
    s = MagicMock()
    s.etran_login = overrides.get("login", "test_login")
    s.etran_password = MagicMock()
    s.etran_password.get_secret_value.return_value = overrides.get("password", "secret")
    s.etran_asu_go_id = overrides.get("asu_go_id", "ASU001")
    return s


class TestBuildAccessParams:
    def test_contains_login(self):
        el = build_access_params(_make_settings())
        assert el.findtext("Login") == "test_login"

    def test_contains_password(self):
        el = build_access_params(_make_settings(password="p@ss"))
        assert el.findtext("Password") == "p@ss"

    def test_contains_asu_go_id(self):
        el = build_access_params(_make_settings(asu_go_id="GO42"))
        assert el.findtext("AsuGoId") == "GO42"


class TestWrapRequest:
    def test_produces_valid_xml(self):
        xml_str = wrap_request("GetNSI", _make_settings())
        root = etree.fromstring(xml_str.encode())
        assert root.tag == "GetNSI"
        assert root.find("AccessParams") is not None

    def test_includes_body(self):
        body = etree.Element("Filter")
        etree.SubElement(body, "Code").text = "123"
        xml_str = wrap_request("GetNSI", _make_settings(), body)
        root = etree.fromstring(xml_str.encode())
        assert root.findtext("Filter/Code") == "123"
