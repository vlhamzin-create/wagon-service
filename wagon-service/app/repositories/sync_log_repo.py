from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_log import SyncLog


class SyncLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[SyncLog]:
        result = await self._session.execute(select(SyncLog).order_by(SyncLog.source))
        return list(result.scalars().all())

    async def upsert(
        self,
        source: str,
        last_status: str,
        last_error: str | None = None,
    ) -> SyncLog:
        from datetime import datetime, timezone

        from sqlalchemy.dialects.postgresql import insert

        now = datetime.now(tz=timezone.utc)
        values: dict = {
            "source": source,
            "last_status": last_status,
            "last_error": last_error,
            "updated_at": now,
        }
        if last_status == "ok":
            values["last_success_at"] = now

        stmt = (
            insert(SyncLog)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["source"],
                set_={k: v for k, v in values.items() if k != "source"},
            )
            .returning(SyncLog)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one()
