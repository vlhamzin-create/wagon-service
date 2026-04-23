from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from etran_adapter.models.base import Base


class RequestLog(Base):
    """Журнал запросов к ЭТРАН для аудита и отладки."""

    __tablename__ = "request_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    correlation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, default=uuid.uuid4, index=True
    )
    operation: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # 'request' | 'response'
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # 'ok' | 'error' | 'timeout'
    request_xml: Mapped[str | None] = mapped_column(Text)
    response_xml: Mapped[str | None] = mapped_column(Text)
    error_detail: Mapped[str | None] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSONB)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
