from __future__ import annotations

from typing import Any

import structlog

from etran_adapter.config import settings
from etran_adapter.operations.registry import get_operation
from etran_adapter.retry.policy import with_etran_retry
from etran_adapter.soap.client import EtranSoapClient

logger = structlog.get_logger(__name__)

_client: EtranSoapClient | None = None


def _get_client() -> EtranSoapClient:
    global _client  # noqa: PLW0603
    if _client is None:
        _client = EtranSoapClient(settings)
    return _client


@with_etran_retry
def execute_etran_operation(
    operation: str,
    params: dict[str, Any],
    callback_url: str | None = None,
) -> str:
    """Исполняемая задача RQ: вызов операции ЭТРАН с retry и callback."""
    logger.info("task.started", operation=operation)

    client = _get_client()
    op = get_operation(operation)
    result = op.execute_async(client=client, params=params)

    if callback_url:
        _send_callback(callback_url, operation, result)

    logger.info("task.completed", operation=operation)
    return result


def _send_callback(url: str, operation: str, result: str) -> None:
    """Отправляет webhook-уведомление в wagon-service."""
    import httpx

    payload = {"operation": operation, "success": True, "data": result}
    try:
        resp = httpx.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except httpx.HTTPError:
        logger.warning("callback.failed", url=url, exc_info=True)
