"""wagon: apply TODO-COL-1/2/3 schema decisions

Revision ID: 0013
Revises: 0012
Create Date: 2026-04-24 00:00:00.000000

Changes
-------
  TODO-COL-1: удалить days_without_movement (INTEGER, хранимое) —
              поле вычисляется на BE из last_movement_at.
              Добавить индекс idx_wagon_last_movement_at для сортировки.

  TODO-COL-2: дублирующее поле supplier отсутствует (не было создано).
              Каноническое поле supplier_name и индекс idx_wagon_supplier_name
              существуют с миграции 0003. Добавлены COMMENT на поля.

  TODO-COL-3: добавить next_destination_station_code (VARCHAR(16)) —
              поле кода следующей станции назначения из RWL.
              Добавить индекс idx_wagon_next_destination.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"
TABLE = "wagon"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # TODO-COL-1: убрать хранимое days_without_movement.
    # Поле вычисляется на BE: CURRENT_DATE - last_movement_at::date.
    # last_movement_at уже присутствует в таблице с 0003.
    # ------------------------------------------------------------------
    op.drop_column(TABLE, "days_without_movement", schema=SCHEMA)

    # Индекс для ORDER BY last_movement_at ASC/DESC NULLS LAST
    # (сортировка по «Дням без движения» в API).
    # Частичный по deleted_at IS NULL — исключаем soft-deleted строки.
    op.create_index(
        index_name="idx_wagon_last_movement_at",
        table_name=TABLE,
        columns=["last_movement_at"],
        schema=SCHEMA,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ------------------------------------------------------------------
    # TODO-COL-3: добавить код следующей станции назначения.
    # next_destination_station_name уже есть (добавлена в 0003).
    # Добавляем парное поле next_destination_station_code.
    # ------------------------------------------------------------------
    op.add_column(
        TABLE,
        sa.Column(
            "next_destination_station_code",
            sa.String(16),
            nullable=True,
            comment="Код следующей станции назначения из RWL (TODO-COL-3)",
        ),
        schema=SCHEMA,
    )

    # Индекс для поиска/фильтрации по следующей станции.
    op.create_index(
        index_name="idx_wagon_next_destination",
        table_name=TABLE,
        columns=["next_destination_station_name"],
        schema=SCHEMA,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # ------------------------------------------------------------------
    # Обновить комментарии к полям, снять TODO-пометки
    # ------------------------------------------------------------------
    op.execute(
        "COMMENT ON COLUMN wagon_service.wagon.supplier_name IS "
        "'Наименование поставщика из RWL. NULL если RWL не передаёт значение. "
        "Закрыто: TODO-COL-2';"
    )
    op.execute(
        "COMMENT ON COLUMN wagon_service.wagon.last_movement_at IS "
        "'Дата и время последнего движения из RWL. "
        "days_without_movement вычисляется на BE: CURRENT_DATE - last_movement_at::date. "
        "Закрыто: TODO-COL-1';"
    )
    op.execute(
        "COMMENT ON COLUMN wagon_service.wagon.next_destination_station_code IS "
        "'Код следующей станции назначения из RWL. Закрыто: TODO-COL-3';"
    )
    op.execute(
        "COMMENT ON COLUMN wagon_service.wagon.next_destination_station_name IS "
        "'Наименование следующей станции назначения из RWL. Закрыто: TODO-COL-3';"
    )


def downgrade() -> None:
    # ------------------------------------------------------------------
    # TODO-COL-3 rollback: удалить next_destination_station_code и индекс
    # ------------------------------------------------------------------
    op.drop_index(
        "idx_wagon_next_destination",
        table_name=TABLE,
        schema=SCHEMA,
    )
    op.drop_column(TABLE, "next_destination_station_code", schema=SCHEMA)

    # ------------------------------------------------------------------
    # TODO-COL-1 rollback: вернуть days_without_movement, удалить индекс
    # Значения будут NULL — данные невосстановимы без повторной синхронизации.
    # ------------------------------------------------------------------
    op.drop_index(
        "idx_wagon_last_movement_at",
        table_name=TABLE,
        schema=SCHEMA,
    )
    op.add_column(
        TABLE,
        sa.Column(
            "days_without_movement",
            sa.Integer(),
            nullable=True,
            comment="ROLLBACK 0013: восстановлено из downgrade, значения NULL",
        ),
        schema=SCHEMA,
    )
