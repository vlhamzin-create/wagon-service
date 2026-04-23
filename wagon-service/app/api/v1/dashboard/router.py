from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TokenPayload
from app.dependencies import get_db, require_roles
from app.api.v1.dashboard.schemas import DashboardBasicResponse
from app.api.v1.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_require_manager = require_roles("Руководитель")


@router.get(
    "/basic",
    response_model=DashboardBasicResponse,
    summary="Базовый дашборд по категориям состояний вагонов",
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
    },
)
async def get_basic_dashboard(
    wagon_type: Annotated[Optional[str], Query(max_length=100, description="Фильтр по типу вагона")] = None,
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(_require_manager),
) -> DashboardBasicResponse:
    service = DashboardService(db)
    data = await service.get_dashboard_data(wagon_type=wagon_type)
    return DashboardBasicResponse(
        calculated_at=datetime.now(timezone.utc),
        **data,
    )
