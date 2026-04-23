from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import CurrentUser
from app.dependencies import get_db, require_roles
from app.schemas.sync_status import SyncStatusResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync-status", tags=["sync"])

# Статус синхронизации — только для операционных ролей
_require_ops = require_roles("Руководитель", "Логист", "Оператор", "Админ")


@router.get("", response_model=SyncStatusResponse, summary="Статус синхронизации с внешними системами")
async def get_sync_status(
    db: AsyncSession = Depends(get_db),
    _user: Annotated[CurrentUser, Depends(_require_ops)] = None,
) -> SyncStatusResponse:
    return await SyncService(db).get_status()
