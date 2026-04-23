from __future__ import annotations

from rq import Worker

from etran_adapter.config import settings
from etran_adapter.infrastructure.redis_ import redis_conn


def main() -> None:
    """Точка входа RQ worker."""
    queues = [settings.rq_high_queue_name, settings.rq_queue_name]
    worker = Worker(queues, connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    main()
