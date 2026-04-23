from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Index, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SCHEMA


class Wagon(Base):
    __tablename__ = "wagon"
    __table_args__ = (
        # Сортировка по умолчанию: destination_railway DESC, destination_station_name ASC
        Index(
            "idx_wagon_sort_default",
            "destination_railway",
            "destination_station_name",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Частичный индекс: только вагоны, требующие распределения
        Index(
            "idx_wagon_requires_assignment",
            "requires_assignment",
            postgresql_where=text("deleted_at IS NULL AND requires_assignment = TRUE"),
        ),
        # Фильтр «Дорога назначения»
        Index(
            "idx_wagon_destination_railway",
            "destination_railway",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Фильтр «Поставщик»
        Index(
            "idx_wagon_supplier_name",
            "supplier_name",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Фильтр «Статус»
        Index(
            "idx_wagon_status",
            "status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Фильтры owner_type / wagon_type
        Index(
            "idx_wagon_owner_type",
            "owner_type",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_wagon_wagon_type",
            "wagon_type",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # LIKE-поиск по номеру вагона (prefix)
        Index(
            "idx_wagon_number_pattern",
            "number",
            postgresql_ops={"number": "varchar_pattern_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # LIKE-поиск по станции назначения
        Index(
            "idx_wagon_destination_station_name_pattern",
            "destination_station_name",
            postgresql_ops={"destination_station_name": "varchar_pattern_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Комбинированный: requires_assignment + destination_railway
        Index(
            "idx_wagon_assignment_railway",
            "requires_assignment",
            "destination_railway",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # current_city — из SRS п. 2.2.5
        Index(
            "idx_wagon_current_city",
            "current_city",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # updated_at — для инкрементальной синхронизации
        Index(
            "idx_wagon_updated_at",
            "updated_at",
            postgresql_using="btree",
        ),
        {"schema": SCHEMA},
    )

    # Идентификация
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id_rwl: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    # Классификация
    owner_type: Mapped[str] = mapped_column(String(32), nullable=False)
    wagon_type: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str | None] = mapped_column(String(64))

    # Технические характеристики
    capacity_tons: Mapped[float | None] = mapped_column(Numeric(10, 2))
    volume_m3: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # Местоположение
    current_country: Mapped[str | None] = mapped_column(String(64))
    current_station_code: Mapped[str | None] = mapped_column(String(16))
    current_station_name: Mapped[str | None] = mapped_column(String(255))
    current_city: Mapped[str | None] = mapped_column(String(255))

    # Станция и дорога назначения
    destination_station_name: Mapped[str | None] = mapped_column(String(255))
    destination_railway: Mapped[str | None] = mapped_column(String(255))

    # TODO-COL-3: следующая станция назначения (источник — RWL, финализированная спецификация)
    next_destination_station_name: Mapped[str | None] = mapped_column(String(255))

    # TODO-COL-1: дни без движения — уточнить: хранимое из RWL или расчётное на BE
    days_without_movement: Mapped[int | None] = mapped_column(Integer)
    last_movement_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # TODO-COL-2: поставщик — уточнить маппинг источника (RWL / 1С / owner_type)
    supplier_name: Mapped[str | None] = mapped_column(String(255))

    # Статус и логика распределения
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    # Вычисляется синхронизатором; не GENERATED — логика пересекает wagon + request
    requires_assignment: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    # Мета
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
