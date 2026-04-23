from __future__ import annotations

import pytest
from lxml import etree

from etran_adapter.soap.envelope import (
    NS_ETRAN,
    NS_SOAP_ENV,
    build_envelope,
    parse_envelope_response,
)
from etran_adapter.soap.exceptions import EtranProtocolError, EtranSoapFaultError


class TestBuildEnvelope:
    def test_produces_valid_soap_xml(self):
        result = build_envelope("GetBlock", "<GetNSI/>")
        root = etree.fromstring(result)
        assert root.tag == f"{{{NS_SOAP_ENV}}}Envelope"

    def test_contains_body_and_header(self):
        result = build_envelope("GetBlock", "<GetNSI/>")
        root = etree.fromstring(result)
        assert root.find(f"{{{NS_SOAP_ENV}}}Header") is not None
        assert root.find(f"{{{NS_SOAP_ENV}}}Body") is not None

    def test_method_element_has_etran_namespace(self):
        result = build_envelope("SendBlock", "<Data/>")
        root = etree.fromstring(result)
        body = root.find(f"{{{NS_SOAP_ENV}}}Body")
        method = body[0]
        assert method.tag == f"{{{NS_ETRAN}}}SendBlock"

    def test_text_payload_inserted_as_text(self):
        payload = "<InvoiceRequest><ID>42</ID></InvoiceRequest>"
        result = build_envelope("GetBlock", payload)
        root = etree.fromstring(result)
        body = root.find(f"{{{NS_SOAP_ENV}}}Body")
        method = body[0]
        text_el = method.find("Text")
        # lxml escapes the XML — it's stored as text content, not parsed
        assert "<InvoiceRequest>" in text_el.text

    def test_base64_payload(self):
        payload = "PHhtbD5kYXRhPC94bWw+"
        result = build_envelope("SendBlock", payload)
        root = etree.fromstring(result)
        body = root.find(f"{{{NS_SOAP_ENV}}}Body")
        text_el = body[0].find("Text")
        assert text_el.text == payload


class TestParseEnvelopeResponse:
    def _wrap_response(self, inner: str) -> bytes:
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f"<soapenv:Envelope xmlns:soapenv=\"{NS_SOAP_ENV}\">"
            f"<soapenv:Body>{inner}</soapenv:Body>"
            f"</soapenv:Envelope>"
        ).encode("utf-8")

    def test_extracts_text_from_response(self):
        inner = f'<ns:{{"GetBlockResponse"}} xmlns:ns="{NS_ETRAN}"><Text>OK</Text></ns:GetBlockResponse>'
        # Simpler approach:
        inner = f'<GetBlockResponse xmlns="{NS_ETRAN}"><Text>some xml data</Text></GetBlockResponse>'
        raw = self._wrap_response(inner)
        result = parse_envelope_response(raw)
        assert result == "some xml data"

    def test_raises_on_soap_fault(self):
        inner = (
            f"<soapenv:Fault xmlns:soapenv=\"{NS_SOAP_ENV}\">"
            "<faultcode>soap:Server</faultcode>"
            "<faultstring>Internal error</faultstring>"
            "</soapenv:Fault>"
        )
        raw = self._wrap_response(inner)
        with pytest.raises(EtranSoapFaultError) as exc_info:
            parse_envelope_response(raw)
        assert exc_info.value.fault_code == "soap:Server"
        assert "Internal error" in exc_info.value.fault_string

    def test_raises_on_invalid_xml(self):
        with pytest.raises(EtranProtocolError, match="Invalid XML"):
            parse_envelope_response(b"not xml at all")

    def test_raises_on_missing_body(self):
        raw = (
            f'<soapenv:Envelope xmlns:soapenv="{NS_SOAP_ENV}">'
            f"</soapenv:Envelope>"
        ).encode()
        with pytest.raises(EtranProtocolError, match="missing Body"):
            parse_envelope_response(raw)

    def test_soap_fault_with_detail(self):
        inner = (
            f"<soapenv:Fault xmlns:soapenv=\"{NS_SOAP_ENV}\">"
            "<faultcode>soap:Client</faultcode>"
            "<faultstring>Bad request</faultstring>"
            "<detail><info>extra</info></detail>"
            "</soapenv:Fault>"
        )
        raw = self._wrap_response(inner)
        with pytest.raises(EtranSoapFaultError) as exc_info:
            parse_envelope_response(raw)
        assert exc_info.value.detail is not None
        assert "extra" in exc_info.value.detail
