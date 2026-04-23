from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def write_audit_entries(
    session: AsyncSession,
    *,
    user_id: uuid.UUID,
    wagon_ids: list[uuid.UUID],
    action: str,
    changes: dict,
    context: dict,
    source: str = "ui",
) -> None:
    """Пишет по одной записи в audit_log для каждого wagon_id.

    Вызывается ВНУТРИ открытой транзакции — commit/rollback на стороне вызывающего.
    """
    entries = [
        AuditLog(
            user_id=user_id,
            entity_type="wagon",
            entity_id=wid,
            action=action,
            changes=changes,
            context=context,
            source=source,
        )
        for wid in wagon_ids
    ]
    session.add_all(entries)
