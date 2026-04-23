from __future__ import annotations

import uuid

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter_preset import FilterPreset
from app.repositories.filter_preset_repo import FilterPresetRepository
from app.schemas.filter_preset import FilterPresetCreate, FilterPresetUpdate
from app.services.audit import write_audit_entries

PRESET_LIMIT_PER_SCOPE = 50


class FilterPresetService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = FilterPresetRepository(session)

    async def create(
        self,
        user_id: uuid.UUID,
        data: FilterPresetCreate,
    ) -> FilterPreset:
        count = await self._repo.count_by_user_scope(user_id, data.scope)
        if count >= PRESET_LIMIT_PER_SCOPE:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Maximum {PRESET_LIMIT_PER_SCOPE} presets per scope allowed",
            )

        preset = FilterPreset(
            user_id=user_id,
            scope=data.scope,
            name=data.name,
            description=data.description,
            filters=data.filters,
        )
        preset = await self._repo.create(preset)

        await write_audit_entries(
            self._session,
            user_id=user_id,
            wagon_ids=[preset.id],
            action="filter_preset.create",
            changes={"name": {"new": data.name}, "scope": {"new": data.scope}},
            context={"entity_type": "filter_preset"},
            source="ui",
        )
        await self._session.commit()
        return preset

    async def list_by_scope(
        self,
        user_id: uuid.UUID,
        scope: str,
    ) -> list[FilterPreset]:
        return await self._repo.list_by_user_scope(user_id, scope)

    async def get_one(
        self,
        user_id: uuid.UUID,
        preset_id: uuid.UUID,
    ) -> FilterPreset:
        preset = await self._repo.get_by_id(preset_id)
        if preset is None or preset.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Filter preset not found",
            )
        return preset

    async def update(
        self,
        user_id: uuid.UUID,
        preset_id: uuid.UUID,
        data: FilterPresetUpdate,
    ) -> FilterPreset:
        preset = await self.get_one(user_id, preset_id)

        changes: dict = {}
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            old = getattr(preset, field)
            if old != value:
                changes[field] = {"old": old, "new": value}
                setattr(preset, field, value)

        if changes:
            await write_audit_entries(
                self._session,
                user_id=user_id,
                wagon_ids=[preset.id],
                action="filter_preset.update",
                changes=changes,
                context={"entity_type": "filter_preset"},
                source="ui",
            )
        await self._session.commit()
        await self._session.refresh(preset)
        return preset

    async def delete(
        self,
        user_id: uuid.UUID,
        preset_id: uuid.UUID,
    ) -> None:
        preset = await self.get_one(user_id, preset_id)

        await write_audit_entries(
            self._session,
            user_id=user_id,
            wagon_ids=[preset.id],
            action="filter_preset.delete",
            changes={"name": {"old": preset.name}},
            context={"entity_type": "filter_preset"},
            source="ui",
        )
        await self._repo.delete_by_id(preset.id)
        await self._session.commit()
