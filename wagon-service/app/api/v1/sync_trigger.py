from __future__ import annotations

import asyncio
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TokenPayload
from app.database import AsyncSessionLocal
from app.dependencies import get_db, require_roles
from app.services.sync_service import SyncService, run_sync_job

log = structlog.get_logger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])

# Только Админ и Оператор могут запускать синхронизацию вручную
_require_trigger = require_roles("Admin", "Оператор", "Админ")


class TriggerResponse(BaseModel):
    detail: str


@router.post(
    "/trigger",
    response_model=TriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ручной запуск синхронизации из RWL и 1С",
)
async def trigger_sync(
    background_tasks: BackgroundTasks,
    _user: Annotated[TokenPayload, Depends(_require_trigger)] = None,
) -> TriggerResponse:
    """Ставит задачу синхронизации в фон и немедленно возвращает 202.

    Статус выполнения можно отслеживать через ``GET /api/v1/sync-status``.
    """
    background_tasks.add_task(run_sync_job, AsyncSessionLocal)
    log.info("sync_trigger.accepted", user=_user.sub if _user else None)
    return TriggerResponse(detail="Sync started")
