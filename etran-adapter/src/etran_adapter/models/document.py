from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from etran_adapter.models.base import Base


class Document(Base):
    """Бизнес-документы ЭТРАН НП. Одна запись = один документ."""

    __tablename__ = "document"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    document_type_code: Mapped[str] = mapped_column(
        String(64), ForeignKey("document_type_dict.code"), nullable=False
    )

    # Идентификаторы в системах
    etran_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    etran_number: Mapped[str | None] = mapped_column(String(64))
    parent_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document.id")
    )

    # Текущий статус
    current_status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'DRAFT'")
    )
    etran_status_raw: Mapped[str | None] = mapped_column(String(64))

    # Бизнес-атрибуты (денормализованы для поиска)
    wagon_number: Mapped[str | None] = mapped_column(String(10))
    container_number: Mapped[str | None] = mapped_column(String(16))
    cargo_code: Mapped[str | None] = mapped_column(String(10))
    sender_station_code: Mapped[str | None] = mapped_column(String(8))
    dest_station_code: Mapped[str | None] = mapped_column(String(8))
    shipper_okpo: Mapped[str | None] = mapped_column(String(16))
    consignee_okpo: Mapped[str | None] = mapped_column(String(16))

    # Привязка к внутренним сущностям
    wagon_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    route_client_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Ссылки на сообщения обмена
    initial_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_exchange.id")
    )
    last_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_exchange.id")
    )

    # ЭП
    requires_signature: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    signed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    signed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Аудит
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )


class DocumentStatusHistory(Base):
    """Полная история переходов статусов каждого документа ЭТРАН."""

    __tablename__ = "document_status_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document.id", ondelete="CASCADE"), nullable=False, index=True
    )

    status_from: Mapped[str | None] = mapped_column(String(32))
    status_to: Mapped[str] = mapped_column(String(32), nullable=False)
    etran_status_raw: Mapped[str | None] = mapped_column(String(64))

    # Источник перехода
    triggered_by: Mapped[str] = mapped_column(String(32), nullable=False)
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("message_exchange.id")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    comment: Mapped[str | None] = mapped_column(Text)

    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
