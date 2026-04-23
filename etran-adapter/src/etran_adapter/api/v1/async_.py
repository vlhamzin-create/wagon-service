from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from etran_adapter.api.deps import get_db, verify_api_key
from etran_adapter.queue.enqueue import enqueue_etran_task
from etran_adapter.schemas.etran_request import EtranAsyncRequest
from etran_adapter.schemas.etran_response import EtranAsyncAccepted, EtranTaskStatus

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/v1/etran/async",
    tags=["async"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=EtranAsyncAccepted, status_code=202)
async def async_call(
    payload: EtranAsyncRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EtranAsyncAccepted:
    """Асинхронный вызов ЭТРАН (создание заявок, накладных, согласование ВПУ).

    Возвращает task_id; wagon-service получает результат через polling или webhook.
    """
    task_id = enqueue_etran_task(
        operation=payload.operation,
        params=payload.params,
        callback_url=payload.callback_url,
        priority=payload.priority,
    )
    return EtranAsyncAccepted(task_id=task_id)


@router.get("/{task_id}", response_model=EtranTaskStatus)
async def get_task_status(task_id: str) -> EtranTaskStatus:
    """Polling-эндпоинт: статус и результат асинхронной задачи."""
    from rq.job import Job

    from etran_adapter.infrastructure.redis_ import redis_conn

    job = Job.fetch(task_id, connection=redis_conn)
    status = job.get_status()
    result = job.result if status == "finished" else None
    error = str(job.exc_info) if status == "failed" else None

    return EtranTaskStatus(
        task_id=task_id,
        status=status,
        result=result,
        error=error,
    )
