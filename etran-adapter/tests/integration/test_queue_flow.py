from __future__ import annotations

"""Интеграционные тесты очереди RQ.

Предполагают запущенный Redis. Пропускаются при его отсутствии.
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("REDIS_URL"),
    reason="REDIS_URL not set — skipping queue integration tests",
)


class TestQueueFlow:
    def test_enqueue_and_fetch_status(self):
        from etran_adapter.queue.enqueue import enqueue_etran_task

        task_id = enqueue_etran_task(operation="nsi", params={"Code": "1"})
        assert isinstance(task_id, str)
        assert len(task_id) > 0
