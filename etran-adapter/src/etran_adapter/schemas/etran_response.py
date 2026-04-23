from __future__ import annotations

from pydantic import BaseModel


class EtranSyncResponse(BaseModel):
    """Ответ синхронного вызова ЭТРАН."""

    success: bool
    operation: str
    data: str  # XML-строка из Text ответа


class EtranAsyncAccepted(BaseModel):
    """Подтверждение постановки задачи в очередь."""

    task_id: str


class EtranTaskStatus(BaseModel):
    """Статус асинхронной задачи (polling)."""

    task_id: str
    status: str  # queued | started | finished | failed
    result: str | None = None
    error: str | None = None
