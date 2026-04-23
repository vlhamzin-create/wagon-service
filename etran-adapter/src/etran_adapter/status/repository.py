from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from etran_adapter.models.document import Document, DocumentStatusHistory
from etran_adapter.status.codes import EtranDocumentStatus, resolve_status


class DocumentStatusRepository:
    """CRUD статусов документов ЭТРАН в БД."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_current_status(self, document_id: uuid.UUID) -> str | None:
        """Получить текущий статус документа."""
        stmt = select(Document.current_status).where(Document.id == document_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        document_id: uuid.UUID,
        new_status: EtranDocumentStatus,
        *,
        etran_status_raw: str | None = None,
        triggered_by: str = "ETRAN_RESPONSE",
        message_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        comment: str | None = None,
    ) -> None:
        """Обновить статус документа и записать историю перехода."""
        current = await self.get_current_status(document_id)

        stmt = (
            update(Document)
            .where(Document.id == document_id)
            .values(
                current_status=new_status.value,
                etran_status_raw=etran_status_raw,
                updated_at=datetime.utcnow(),
            )
        )
        await self._session.execute(stmt)

        history = DocumentStatusHistory(
            document_id=document_id,
            status_from=current,
            status_to=new_status.value,
            etran_status_raw=etran_status_raw,
            triggered_by=triggered_by,
            message_id=message_id,
            user_id=user_id,
            comment=comment,
        )
        self._session.add(history)
        await self._session.flush()

    async def update_status_from_etran_code(
        self,
        document_id: uuid.UUID,
        etran_code: str,
        *,
        message_id: uuid.UUID | None = None,
    ) -> EtranDocumentStatus:
        """Резолвить код ЭТРАН в статус и обновить документ."""
        resolved = resolve_status(etran_code)
        await self.update_status(
            document_id,
            resolved,
            etran_status_raw=etran_code,
            triggered_by="ETRAN_RESPONSE",
            message_id=message_id,
        )
        return resolved

    async def get_status_history(
        self, document_id: uuid.UUID
    ) -> list[DocumentStatusHistory]:
        """Получить историю переходов статусов документа."""
        stmt = (
            select(DocumentStatusHistory)
            .where(DocumentStatusHistory.document_id == document_id)
            .order_by(DocumentStatusHistory.occurred_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
