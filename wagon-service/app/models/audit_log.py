from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Identity, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SCHEMA


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        Index(
            "ix_audit_log_entity",
            "entity_type",
            "entity_id",
            "event_time",
        ),
        Index(
            "ix_audit_log_user_time",
            "user_id",
            "event_time",
        ),
        Index(
            "ix_audit_log_changes_gin",
            "changes",
            postgresql_using="gin",
        ),
        {"schema": SCHEMA},
    )

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=False), primary_key=True
    )
    event_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default="now()",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    context: Mapped[dict | None] = mapped_column(JSONB(astext_type=Text()))
    changes: Mapped[dict | None] = mapped_column(JSONB(astext_type=Text()))
    source: Mapped[str | None] = mapped_column(String(64))
