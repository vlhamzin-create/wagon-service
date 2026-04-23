from __future__ import annotations

"""Интеграционные тесты SOAP-клиента.

Предполагают наличие ЭТРАН sandbox или WireMock.
Пропускаются при отсутствии переменной ETRAN_TEST_WSDL.
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("ETRAN_TEST_WSDL"),
    reason="ETRAN_TEST_WSDL not set — skipping integration tests",
)


class TestSoapClientIntegration:
    def test_ping(self):
        from etran_adapter.config import settings
        from etran_adapter.soap.client import EtranSoapClient

        client = EtranSoapClient(settings)
        assert client.ping() is True
