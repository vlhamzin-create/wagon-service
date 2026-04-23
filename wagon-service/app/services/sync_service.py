from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sync_log_repo import SyncLogRepository
from app.schemas.sync_status import SourceStatus, SyncStatusResponse


class SyncService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = SyncLogRepository(session)

    async def get_status(self) -> SyncStatusResponse:
        logs = await self._repo.get_all()
        return SyncStatusResponse(
            sources=[
                SourceStatus(
                    source=log.source,
                    last_success_at=log.last_success_at,
                    last_status=log.last_status,
                    last_error=log.last_error,
                )
                for log in logs
            ]
        )
