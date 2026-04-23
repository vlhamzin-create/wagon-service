from __future__ import annotations

import pytest
from zeep.exceptions import TransportError

from etran_adapter.retry.policy import with_etran_retry
from etran_adapter.soap.xml_parser import EtranResponseError


class TestRetryPolicy:
    def test_succeeds_without_retry(self):
        call_count = 0

        @with_etran_retry
        def ok():
            nonlocal call_count
            call_count += 1
            return "done"

        assert ok() == "done"
        assert call_count == 1

    def test_retries_on_transport_error(self):
        call_count = 0

        @with_etran_retry
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TransportError(status_code=503, message="unavailable")
            return "recovered"

        assert flaky() == "recovered"
        assert call_count == 3

    def test_gives_up_after_max_attempts(self):
        @with_etran_retry
        def always_fails():
            raise TransportError(status_code=503, message="down")

        with pytest.raises(TransportError):
            always_fails()
