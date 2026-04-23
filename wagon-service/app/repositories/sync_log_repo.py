from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_log import SyncLog


class SyncLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Семантические методы (предпочтительный интерфейс)
    # ------------------------------------------------------------------

    async def upsert_running(self, source: str) -> None:
        """Фиксирует старт синхронизации — статус 'running'."""
        await self._upsert(source, status="running", error=None, update_success=False)

    async def upsert_success(self, source: str) -> None:
        """Фиксирует успех — обновляет last_success_at."""
        await self._upsert(source, status="success", error=None, update_success=True)

    async def upsert_error(self, source: str, error: str) -> None:
        """Фиксирует ошибку — last_success_at НЕ изменяется."""
        await self._upsert(source, status="error", error=error, update_success=False)

    # ------------------------------------------------------------------
    # Низкоуровневый upsert (публичный для обратной совместимости)
    # ------------------------------------------------------------------

    async def upsert(
        self,
        source: str,
        last_status: str,
        last_error: str | None = None,
    ) -> SyncLog:
        """Generic upsert; возвращает обновлённую запись.

        ``last_success_at`` обновляется только если ``last_status == 'success'``.
        """
        update_success = last_status == "success"
        return await self._upsert(
            source,
            status=last_status,
            error=last_error,
            update_success=update_success,
            returning=True,
        )

    # ------------------------------------------------------------------
    # Запросы
    # ------------------------------------------------------------------

    async def get_all(self) -> list[SyncLog]:
        result = await self._session.execute(select(SyncLog).order_by(SyncLog.source))
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Внутренние методы
    # ------------------------------------------------------------------

    async def _upsert(
        self,
        source: str,
        status: str,
        error: str | None,
        update_success: bool,
        returning: bool = False,
    ) -> SyncLog | None:
        now = datetime.now(tz=timezone.utc)

        insert_values: dict = {
            "source": source,
            "last_status": status,
            "last_error": error,
            "last_success_at": now if update_success else None,
            "updated_at": now,
        }

        set_values: dict = {
            "last_status": status,
            "last_error": error,
            "updated_at": now,
        }
        if update_success:
            set_values["last_success_at"] = now

        stmt = (
            insert(SyncLog)
            .values(**insert_values)
            .on_conflict_do_update(
                index_elements=["source"],
                set_=set_values,
            )
        )

        if returning:
            stmt = stmt.returning(SyncLog)
            result = await self._session.execute(stmt)
            await self._session.commit()
            return result.scalar_one()

        await self._session.execute(stmt)
        await self._session.commit()
        return None
