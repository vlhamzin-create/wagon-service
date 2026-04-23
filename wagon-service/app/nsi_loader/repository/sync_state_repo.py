from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dicts import NsiSyncState


class SyncStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, dictionary_name: str) -> NsiSyncState | None:
        stmt = select(NsiSyncState).where(
            NsiSyncState.dictionary_name == dictionary_name
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_running(self, dictionary_name: str) -> None:
        stmt = (
            update(NsiSyncState)
            .where(NsiSyncState.dictionary_name == dictionary_name)
            .values(status="running", last_error=None)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def set_success(
        self,
        dictionary_name: str,
        records_total: int,
        records_upserted: int,
        last_chg_dt: Optional[str] = None,
    ) -> None:
        values: dict = {
            "status": "success",
            "last_sync_at": datetime.now(timezone.utc),
            "records_total": records_total,
            "records_upserted": records_upserted,
            "last_error": None,
        }
        if last_chg_dt is not None:
            values["last_chg_dt"] = last_chg_dt
        stmt = (
            update(NsiSyncState)
            .where(NsiSyncState.dictionary_name == dictionary_name)
            .values(**values)
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def set_error(self, dictionary_name: str, error: str) -> None:
        stmt = (
            update(NsiSyncState)
            .where(NsiSyncState.dictionary_name == dictionary_name)
            .values(status="error", last_error=error[:4000])
        )
        await self._session.execute(stmt)
        await self._session.commit()
