from __future__ import annotations

from typing import Any

from rq import Queue, Retry

from etran_adapter.config import settings
from etran_adapter.infrastructure.redis_ import redis_conn

_default_queue = Queue(settings.rq_queue_name, connection=redis_conn)
_high_queue = Queue(settings.rq_high_queue_name, connection=redis_conn)

_HIGH_PRIORITY_OPS = {"nsi"}


def enqueue_etran_task(
    operation: str,
    params: dict[str, Any],
    callback_url: str | None = None,
    priority: str = "default",
) -> str:
    """Ставит задачу в RQ и возвращает job_id."""
    queue = _high_queue if priority == "high" or operation in _HIGH_PRIORITY_OPS else _default_queue

    job = queue.enqueue(
        "etran_adapter.queue.tasks.execute_etran_operation",
        operation=operation,
        params=params,
        callback_url=callback_url,
        result_ttl=settings.task_result_ttl_seconds,
        retry=Retry(max=settings.etran_max_retries, interval=[30, 60, 120]),
    )
    return job.id
