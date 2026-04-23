from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SCHEMA


class Request(Base):
    __tablename__ = "request"
    __table_args__ = (
        # FK к wagon — обязателен для ON DELETE SET NULL без sequential scan
        Index(
            "idx_request_wagon_assigned_id",
            "wagon_assigned_id",
            postgresql_where=text("wagon_assigned_id IS NOT NULL"),
        ),
        # Незакрытые заявки без вагона — ядро вычисления requires_assignment
        Index(
            "idx_request_unassigned",
            "status",
            "planned_date",
            postgresql_where=text("wagon_assigned_id IS NULL"),
        ),
        # Фильтр «Клиент»
        Index("idx_request_client_name", "client_name"),
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Внешний идентификатор из 1С; используется для upsert при синхронизации
    external_id_1c: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    # Клиент (источник — 1С)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Параметры заявки
    required_wagon_type: Mapped[str] = mapped_column(String(32), nullable=False)
    origin_station_code: Mapped[str] = mapped_column(String(16), nullable=False)
    destination_station_code: Mapped[str] = mapped_column(String(16), nullable=False)
    planned_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Назначение вагона: NULL = вагон не назначен → участвует в вычислении requires_assignment
    wagon_assigned_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{SCHEMA}.wagon.id",
            name="fk_request_wagon_assigned_id_wagon",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
    )

    # Статус (зеркало 1С)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'Новая'")
    )

    # Мета
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
