from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.integrations.exceptions import (
    OneCServerError,
    OneCUnavailableError,
    OneCValidationError,
)
from app.integrations.onec_client import OneCAssignmentPayload, OneCClient
from app.models.assignment_sync_log import AssignmentSyncLog
from app.models.wagon import Wagon
from app.repositories.assignment_sync_log_repo import AssignmentSyncLogRepository

log = structlog.get_logger(__name__)


class OneCAssignmentService:
    """Оркестрирует отправку назначений в 1С с retry и логированием."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = AssignmentSyncLogRepository(session)
        self._client = OneCClient()

    async def create_sync_entry(
        self, assignment_id: uuid.UUID
    ) -> AssignmentSyncLog:
        return await self._repo.create_pending(assignment_id)

    async def send_to_1c(
        self,
        sync_log: AssignmentSyncLog,
        wagon_ids: list[uuid.UUID],
        station_code: str | None,
        client_external_id: str | None,
        user_id: uuid.UUID,
        comment: str | None = None,
    ) -> None:
        log_id = sync_log.id
        attempt = sync_log.attempt_count + 1
        max_attempts = settings.onec_assignment_max_retries

        bound = log.bind(
            sync_log_id=str(log_id),
            assignment_id=str(sync_log.assignment_id),
            attempt=attempt,
        )

        await self._repo.mark_in_progress(log_id, attempt)

        payload = OneCAssignmentPayload(
            idempotency_key=f"{log_id}:{attempt}",
            wagon_ids=[str(w) for w in wagon_ids],
            station_code=station_code,
            client_external_id=client_external_id,
            comment=comment,
            assigned_at=datetime.now(tz=timezone.utc).isoformat(),
            assigned_by_user_id=str(user_id),
        )

        try:
            resp = await self._client.send_assignment(payload)
        except OneCValidationError as exc:
            bound.warning(
                "onec_assignment.validation_error",
                error=str(exc),
            )
            await self._repo.mark_permanently_failed(log_id, str(exc))
            await self._update_wagon_sync_status(
                wagon_ids, "FAILED", synced_at=None
            )
            return
        except (OneCUnavailableError, OneCServerError) as exc:
            response_code = getattr(exc, "status_code", None)
            response_body = getattr(exc, "response_body", None)

            if attempt >= max_attempts:
                bound.error(
                    "onec_assignment.max_retries_exceeded",
                    error=str(exc),
                )
                await self._repo.mark_permanently_failed(log_id, str(exc))
                await self._update_wagon_sync_status(
                    wagon_ids, "FAILED", synced_at=None
                )
                return

            retry_delay = settings.onec_assignment_retry_base_seconds * (
                2 ** (attempt - 1)
            )
            next_retry = datetime.now(tz=timezone.utc) + timedelta(
                seconds=retry_delay
            )
            bound.warning(
                "onec_assignment.retry_scheduled",
                error=str(exc),
                next_retry_at=next_retry.isoformat(),
            )
            await self._repo.mark_failed_attempt(
                log_id,
                error_message=str(exc),
                response_code=response_code,
                body=response_body,
                next_retry_at=next_retry,
            )
            await self._update_wagon_sync_status(
                wagon_ids, "PENDING", synced_at=None
            )
            return
        except Exception as exc:
            bound.exception("onec_assignment.unexpected_error")
            await self._repo.mark_permanently_failed(log_id, str(exc))
            await self._update_wagon_sync_status(
                wagon_ids, "FAILED", synced_at=None
            )
            return

        # Success
        bound.info(
            "onec_assignment.success",
            onec_doc_id=resp.onec_document_id,
        )
        await self._repo.mark_success(log_id, resp.status_code, resp.message)
        now = datetime.now(tz=timezone.utc)
        await self._update_wagon_sync_status(
            wagon_ids, "SUCCESS", synced_at=now
        )

    async def _update_wagon_sync_status(
        self,
        wagon_ids: list[uuid.UUID],
        status: str,
        synced_at: datetime | None,
    ) -> None:
        values: dict = {"onec_sync_status": status}
        if synced_at is not None:
            values["onec_synced_at"] = synced_at
        await self._session.execute(
            update(Wagon).where(Wagon.id.in_(wagon_ids)).values(**values)
        )
        await self._session.commit()


# ------------------------------------------------------------------
# Фоновая задача: retry неотправленных назначений
# ------------------------------------------------------------------


async def retry_pending_assignments(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Подбирает записи PENDING с истёкшим next_retry_at и повторяет отправку."""
    now = datetime.now(tz=timezone.utc)
    async with session_factory() as session:
        repo = AssignmentSyncLogRepository(session)
        pending = await repo.get_pending_for_retry(now)

        if not pending:
            return

        log.info("onec_retry.start", count=len(pending))

        for entry in pending:
            try:
                service = OneCAssignmentService(session)
                # Загружаем wagon_ids из assignment_id — это id batch-операции,
                # данные для payload нужно восстановить из sync_log
                await service.send_to_1c(
                    sync_log=entry,
                    wagon_ids=[entry.assignment_id],
                    station_code=None,
                    client_external_id=None,
                    user_id=uuid.UUID(int=0),
                    comment=None,
                )
            except Exception:
                log.exception(
                    "onec_retry.entry_error",
                    sync_log_id=str(entry.id),
                )

        log.info("onec_retry.done")
