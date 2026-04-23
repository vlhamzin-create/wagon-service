from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TokenPayload
from app.dependencies import get_db, require_any_role
from app.schemas.filter_preset import (
    FilterPresetCreate,
    FilterPresetResponse,
    FilterPresetUpdate,
)
from app.services.filter_preset_service import FilterPresetService

router = APIRouter(prefix="/filter-presets", tags=["filter-presets"])


def _user_id(user: TokenPayload) -> uuid.UUID:
    return uuid.UUID(user.sub) if user.sub else uuid.uuid4()


@router.post(
    "",
    response_model=FilterPresetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пресет фильтров",
)
async def create_preset(
    body: FilterPresetCreate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_any_role),
) -> FilterPresetResponse:
    preset = await FilterPresetService(db).create(_user_id(user), body)
    return FilterPresetResponse.model_validate(preset)


@router.get(
    "",
    response_model=list[FilterPresetResponse],
    summary="Список пресетов фильтров текущего пользователя по scope",
)
async def list_presets(
    scope: Annotated[str, Query(max_length=64, description="Scope пресетов")],
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_any_role),
) -> list[FilterPresetResponse]:
    presets = await FilterPresetService(db).list_by_scope(
        _user_id(user), scope
    )
    return [FilterPresetResponse.model_validate(p) for p in presets]


@router.get(
    "/{preset_id}",
    response_model=FilterPresetResponse,
    summary="Получить пресет фильтров по ID",
)
async def get_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_any_role),
) -> FilterPresetResponse:
    preset = await FilterPresetService(db).get_one(
        _user_id(user), preset_id
    )
    return FilterPresetResponse.model_validate(preset)


@router.put(
    "/{preset_id}",
    response_model=FilterPresetResponse,
    summary="Обновить пресет фильтров",
)
async def update_preset(
    preset_id: uuid.UUID,
    body: FilterPresetUpdate,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_any_role),
) -> FilterPresetResponse:
    preset = await FilterPresetService(db).update(
        _user_id(user), preset_id, body
    )
    return FilterPresetResponse.model_validate(preset)


@router.delete(
    "/{preset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пресет фильтров",
)
async def delete_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(require_any_role),
) -> None:
    await FilterPresetService(db).delete(_user_id(user), preset_id)
