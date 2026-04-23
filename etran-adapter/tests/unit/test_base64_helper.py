from __future__ import annotations

from etran_adapter.soap.base64_helper import decode_text, encode_text, is_base64


class TestEncodeText:
    def test_encodes_simple_string(self):
        result = encode_text("hello")
        assert result == "aGVsbG8="

    def test_encodes_xml(self):
        xml = "<Data><ID>1</ID></Data>"
        encoded = encode_text(xml)
        assert decode_text(encoded) == xml

    def test_encodes_cyrillic(self):
        text = "Привет"
        encoded = encode_text(text)
        assert decode_text(encoded) == text


class TestDecodeText:
    def test_decodes_valid_base64(self):
        assert decode_text("aGVsbG8=") == "hello"


class TestIsBase64:
    def test_valid_base64(self):
        assert is_base64("aGVsbG8=") is True

    def test_xml_is_not_base64(self):
        assert is_base64("<Data>123</Data>") is False

    def test_empty_string(self):
        assert is_base64("") is False

    def test_not_multiple_of_4(self):
        assert is_base64("abc") is False

    def test_valid_long_base64(self):
        encoded = encode_text("<SomeXml>data</SomeXml>")
        assert is_base64(encoded) is True
