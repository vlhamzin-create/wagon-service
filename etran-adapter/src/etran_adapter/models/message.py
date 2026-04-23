from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from etran_adapter.models.base import Base


class MessageExchange(Base):
    """Журнал всех входящих и исходящих SOAP-сообщений с ЭТРАН НП."""

    __tablename__ = "message_exchange"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    direction: Mapped[str] = mapped_column(String(16), nullable=False)
    processing_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING'")
    )

    # Привязка к API
    api_method: Mapped[str] = mapped_column(String(16), nullable=False)
    operation_code: Mapped[str | None] = mapped_column(String(64))
    document_type_code: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("document_type_dict.code")
    )

    # Привязка к бизнес-сущностям
    etran_doc_id: Mapped[str | None] = mapped_column(String(64))
    wagon_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    related_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_exchange.id")
    )

    # Содержимое
    raw_xml: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_attributes: Mapped[dict | None] = mapped_column(JSONB)
    error_details: Mapped[dict | None] = mapped_column(JSONB)

    # ЭП
    has_signature: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    signature_version: Mapped[int | None] = mapped_column(SmallInteger)
    signature_verified: Mapped[bool | None] = mapped_column(Boolean)

    # Аудит
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"), index=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    source_system: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default=text("'wagon-service'")
    )
