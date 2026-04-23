from __future__ import annotations

import structlog
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from zeep.exceptions import TransportError

from etran_adapter.soap.xml_parser import EtranResponseError

logger = structlog.get_logger(__name__)

# Коды ошибок ЭТРАН, при которых повтор имеет смысл
_RETRYABLE_ETRAN_CODES = {"BUSY", "TIMEOUT", "SERVICE_UNAVAILABLE"}


def _is_retryable_etran_error(exc: BaseException) -> bool:
    if isinstance(exc, TransportError):
        return True
    if isinstance(exc, EtranResponseError) and exc.code in _RETRYABLE_ETRAN_CODES:
        return True
    return False


with_etran_retry = retry(
    retry=retry_if_exception_type((TransportError, ConnectionError, OSError))
    | retry_if_exception_type(EtranResponseError).with_predicate(_is_retryable_etran_error),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    before_sleep=lambda rs: logger.warning(
        "etran_retry",
        attempt=rs.attempt_number,
        wait=rs.next_action.sleep,
    ),
    reraise=True,
)
