from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter_preset import FilterPreset


class FilterPresetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, preset: FilterPreset) -> FilterPreset:
        self._session.add(preset)
        await self._session.flush()
        await self._session.refresh(preset)
        return preset

    async def get_by_id(
        self, preset_id: uuid.UUID
    ) -> FilterPreset | None:
        return await self._session.get(FilterPreset, preset_id)

    async def list_by_user_scope(
        self,
        user_id: uuid.UUID,
        scope: str,
    ) -> list[FilterPreset]:
        stmt = (
            select(FilterPreset)
            .where(
                FilterPreset.user_id == user_id,
                FilterPreset.scope == scope,
            )
            .order_by(FilterPreset.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user_scope(
        self, user_id: uuid.UUID, scope: str
    ) -> int:
        stmt = select(func.count()).where(
            FilterPreset.user_id == user_id,
            FilterPreset.scope == scope,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def delete_by_id(self, preset_id: uuid.UUID) -> None:
        stmt = delete(FilterPreset).where(FilterPreset.id == preset_id)
        await self._session.execute(stmt)
