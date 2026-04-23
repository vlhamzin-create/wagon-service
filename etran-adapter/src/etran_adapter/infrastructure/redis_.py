from __future__ import annotations

from redis import Redis

from etran_adapter.config import settings

redis_conn = Redis.from_url(settings.redis_url)
