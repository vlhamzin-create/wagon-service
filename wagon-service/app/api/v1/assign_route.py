from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TokenPayload
from app.dependencies import get_db, require_roles
from app.schemas.assign_route import AssignRouteRequest, AssignRouteResponse
from app.services.assign_route import AssignRouteService

router = APIRouter(tags=["wagons"])


@router.post(
    "/assign-route",
    response_model=AssignRouteResponse,
    summary="Назначение маршрута вагонам (одиночное и массовое)",
)
async def assign_route(
    body: AssignRouteRequest,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_roles("Логист", "Руководитель", "Админ")),
) -> AssignRouteResponse:
    user_id = uuid.UUID(user.sub) if user.sub else uuid.uuid4()
    return await AssignRouteService(db).assign(body, user_id=user_id)
