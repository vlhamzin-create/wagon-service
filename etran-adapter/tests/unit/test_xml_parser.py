from __future__ import annotations

import pytest

from etran_adapter.soap.xml_parser import EtranResponseError, extract_text, parse_response


class TestParseResponse:
    def test_returns_root_on_success(self):
        xml = "<Response><Status>OK</Status></Response>"
        root = parse_response(xml)
        assert root.tag == "Response"

    def test_raises_on_error(self):
        xml = (
            "<Response>"
            "<Error><Code>AUTH</Code><Message>Bad credentials</Message></Error>"
            "</Response>"
        )
        with pytest.raises(EtranResponseError) as exc_info:
            parse_response(xml)
        assert exc_info.value.code == "AUTH"
        assert "Bad credentials" in str(exc_info.value)

    def test_raises_with_unknown_code(self):
        xml = "<Response><Error></Error></Response>"
        with pytest.raises(EtranResponseError) as exc_info:
            parse_response(xml)
        assert exc_info.value.code == "UNKNOWN"


class TestExtractText:
    def test_existing_element(self):
        from lxml import etree

        root = etree.fromstring(b"<R><Name>Test</Name></R>")
        assert extract_text(root, "Name") == "Test"

    def test_missing_element_returns_default(self):
        from lxml import etree

        root = etree.fromstring(b"<R></R>")
        assert extract_text(root, "Missing", default="N/A") == "N/A"
