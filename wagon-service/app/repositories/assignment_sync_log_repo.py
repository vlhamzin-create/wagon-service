from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assignment_sync_log import AssignmentSyncLog


class AssignmentSyncLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_pending(self, assignment_id: UUID) -> AssignmentSyncLog:
        entry = AssignmentSyncLog(
            assignment_id=assignment_id,
            status="PENDING",
            idempotency_key=f"{assignment_id}:0",
        )
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def mark_in_progress(self, log_id: UUID, attempt: int) -> None:
        now = datetime.now(tz=timezone.utc)
        await self._session.execute(
            update(AssignmentSyncLog)
            .where(AssignmentSyncLog.id == log_id)
            .values(
                status="IN_PROGRESS",
                attempt_count=attempt,
                last_attempt_at=now,
                idempotency_key=f"{log_id}:{attempt}",
                updated_at=now,
            )
        )
        await self._session.commit()

    async def mark_success(
        self, log_id: UUID, response_code: int, body: str
    ) -> None:
        now = datetime.now(tz=timezone.utc)
        await self._session.execute(
            update(AssignmentSyncLog)
            .where(AssignmentSyncLog.id == log_id)
            .values(
                status="SUCCESS",
                onec_response_code=response_code,
                onec_response_body=body[:10_000],
                updated_at=now,
            )
        )
        await self._session.commit()

    async def mark_failed_attempt(
        self,
        log_id: UUID,
        error_message: str,
        response_code: int | None,
        body: str | None,
        next_retry_at: datetime,
    ) -> None:
        now = datetime.now(tz=timezone.utc)
        await self._session.execute(
            update(AssignmentSyncLog)
            .where(AssignmentSyncLog.id == log_id)
            .values(
                status="PENDING",
                error_message=error_message,
                onec_response_code=response_code,
                onec_response_body=(body or "")[:10_000],
                next_retry_at=next_retry_at,
                updated_at=now,
            )
        )
        await self._session.commit()

    async def mark_permanently_failed(
        self, log_id: UUID, error_message: str
    ) -> None:
        now = datetime.now(tz=timezone.utc)
        await self._session.execute(
            update(AssignmentSyncLog)
            .where(AssignmentSyncLog.id == log_id)
            .values(
                status="FAILED",
                error_message=error_message,
                next_retry_at=None,
                updated_at=now,
            )
        )
        await self._session.commit()

    async def get_by_assignment(
        self, assignment_id: UUID
    ) -> AssignmentSyncLog | None:
        result = await self._session.execute(
            select(AssignmentSyncLog).where(
                AssignmentSyncLog.assignment_id == assignment_id
            )
        )
        return result.scalar_one_or_none()

    async def get_pending_for_retry(
        self, now: datetime, limit: int = 50
    ) -> list[AssignmentSyncLog]:
        result = await self._session.execute(
            select(AssignmentSyncLog)
            .where(
                AssignmentSyncLog.status == "PENDING",
                AssignmentSyncLog.next_retry_at.isnot(None),
                AssignmentSyncLog.next_retry_at <= now,
            )
            .order_by(AssignmentSyncLog.next_retry_at)
            .limit(limit)
        )
        return list(result.scalars().all())
