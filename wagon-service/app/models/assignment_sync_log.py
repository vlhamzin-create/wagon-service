from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Index, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SCHEMA


class AssignmentSyncLog(Base):
    __tablename__ = "assignment_1c_sync_log"
    __table_args__ = (
        Index("idx_sync_log_status", "status"),
        Index("idx_sync_log_assignment", "assignment_id"),
        Index(
            "idx_sync_log_next_retry",
            "next_retry_at",
            postgresql_where=text("status IN ('PENDING', 'FAILED')"),
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'PENDING'")
    )
    attempt_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
    max_attempts: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("5")
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    next_retry_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    onec_response_code: Mapped[int | None] = mapped_column(SmallInteger)
    onec_response_body: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(128), unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
