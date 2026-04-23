from __future__ import annotations

from typing import Any, Sequence

from pydantic import BaseModel
from sqlalchemy import Table, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession


class BaseNsiRepository:
    """Базовый репозиторий для НСИ-справочников.

    Предоставляет батч-upsert через INSERT ... ON CONFLICT DO UPDATE.
    """

    def __init__(
        self,
        session: AsyncSession,
        table: Table,
        conflict_column: str,
    ) -> None:
        self._session = session
        self._table = table
        self._conflict_col = conflict_column

    async def upsert_batch(
        self,
        records: Sequence[BaseModel],
        update_columns: list[str],
    ) -> int:
        """Upsert пакета записей.  Возвращает количество затронутых строк."""
        if not records:
            return 0

        rows: list[dict[str, Any]] = [r.model_dump() for r in records]

        set_clause = {
            col: getattr(pg_insert(self._table).excluded, col)
            for col in update_columns
        }
        set_clause["updated_at"] = text("now()")

        stmt = (
            pg_insert(self._table)
            .values(rows)
            .on_conflict_do_update(
                index_elements=[self._conflict_col],
                set_=set_clause,
            )
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount  # type: ignore[return-value]
