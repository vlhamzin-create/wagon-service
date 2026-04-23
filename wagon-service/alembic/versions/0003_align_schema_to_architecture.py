"""Align wagon/request/sync_log schema to agreed architecture

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-03 00:00:00.000000

Changes
-------
wagon:
  - ADD COLUMN destination_station_name, destination_railway,
              next_destination_station_name, days_without_movement,
              last_movement_at, supplier_name
  - ADD UNIQUE CONSTRAINT on external_id_rwl, number
  - DROP legacy simple indexes; ADD optimised partial/composite indexes
request:
  - DROP old table (wagon_id / created_by / notes model)
  - CREATE new table matching architecture
    (external_id_1c, client_name, required_wagon_type, planned_date,
     wagon_assigned_id FK SET NULL)
sync_log:
  - INSERT initial rows for RWL / 1C (idempotent via ON CONFLICT DO NOTHING)
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # wagon: новые колонки
    # ------------------------------------------------------------------
    op.add_column(
        "wagon",
        sa.Column("destination_station_name", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("destination_railway", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        # TODO-COL-3: следующая станция назначения (финализированная спецификация)
        sa.Column("next_destination_station_name", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        # TODO-COL-1: хранимое из RWL; уточнить расчётное vs хранимое
        sa.Column("days_without_movement", sa.Integer(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column(
            "last_movement_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        # TODO-COL-2: поставщик — уточнить маппинг источника
        sa.Column("supplier_name", sa.String(255), nullable=True),
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------
    # wagon: уникальные ограничения (могут отсутствовать в 0001)
    # ------------------------------------------------------------------
    op.create_unique_constraint(
        "uq_wagon_external_id_rwl", "wagon", ["external_id_rwl"], schema=SCHEMA
    )
    op.create_unique_constraint(
        "uq_wagon_number", "wagon", ["number"], schema=SCHEMA
    )

    # ------------------------------------------------------------------
    # wagon: удаляем устаревшие простые индексы из 0001
    # (заменяются оптимизированными частичными/составными ниже)
    # ------------------------------------------------------------------
    _legacy = [
        "ix_wagon_service_wagon_wagon_type",
        "ix_wagon_service_wagon_current_station_name",
        "ix_wagon_service_wagon_current_city",
        "ix_wagon_service_wagon_status",
        "ix_wagon_service_wagon_requires_assignment",
    ]
    for idx_name in _legacy:
        op.drop_index(idx_name, table_name="wagon", schema=SCHEMA, if_exists=True)

    # ------------------------------------------------------------------
    # wagon: оптимизированные индексы
    # ------------------------------------------------------------------

    # Сортировка по умолчанию: destination_railway DESC, destination_station_name ASC
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_sort_default
            ON {SCHEMA}.wagon (destination_railway DESC NULLS LAST, destination_station_name ASC NULLS LAST)
            WHERE deleted_at IS NULL
        """
    )

    # Режим «Требующие распределения»
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_requires_assignment
            ON {SCHEMA}.wagon (requires_assignment)
            WHERE deleted_at IS NULL AND requires_assignment = TRUE
        """
    )

    # Фильтр «Дорога назначения»
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_destination_railway
            ON {SCHEMA}.wagon (destination_railway)
            WHERE deleted_at IS NULL
        """
    )

    # Фильтр «Поставщик»
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_supplier_name
            ON {SCHEMA}.wagon (supplier_name)
            WHERE deleted_at IS NULL
        """
    )

    # Фильтр «Статус»
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_status
            ON {SCHEMA}.wagon (status)
            WHERE deleted_at IS NULL
        """
    )

    # Фильтры owner_type / wagon_type
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_owner_type
            ON {SCHEMA}.wagon (owner_type)
            WHERE deleted_at IS NULL
        """
    )
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_wagon_type
            ON {SCHEMA}.wagon (wagon_type)
            WHERE deleted_at IS NULL
        """
    )

    # LIKE-поиск по номеру вагона (prefix-поиск)
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_number_pattern
            ON {SCHEMA}.wagon (number varchar_pattern_ops)
            WHERE deleted_at IS NULL
        """
    )

    # LIKE-поиск по станции назначения
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_destination_station_name_pattern
            ON {SCHEMA}.wagon (destination_station_name varchar_pattern_ops)
            WHERE deleted_at IS NULL
        """
    )

    # Комбинированный: requires_assignment + destination_railway
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_assignment_railway
            ON {SCHEMA}.wagon (requires_assignment, destination_railway)
            WHERE deleted_at IS NULL
        """
    )

    # current_city — из SRS п. 2.2.5
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_current_city
            ON {SCHEMA}.wagon (current_city)
            WHERE deleted_at IS NULL
        """
    )

    # updated_at — инкрементальная синхронизация
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_updated_at
            ON {SCHEMA}.wagon (updated_at DESC)
        """
    )

    # ------------------------------------------------------------------
    # request: пересоздать под согласованную архитектуру
    # ------------------------------------------------------------------
    op.drop_table("request", schema=SCHEMA)

    op.create_table(
        "request",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("external_id_1c", sa.String(64), nullable=False),
        sa.Column("client_name", sa.String(255), nullable=False),
        sa.Column("required_wagon_type", sa.String(32), nullable=False),
        sa.Column("origin_station_code", sa.String(16), nullable=False),
        sa.Column("destination_station_code", sa.String(16), nullable=False),
        sa.Column("planned_date", sa.Date(), nullable=False),
        sa.Column("wagon_assigned_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'Новая'"),
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_request"),
        sa.UniqueConstraint("external_id_1c", name="uq_request_external_id_1c"),
        sa.ForeignKeyConstraint(
            ["wagon_assigned_id"],
            [f"{SCHEMA}.wagon.id"],
            name="fk_request_wagon_assigned_id_wagon",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        schema=SCHEMA,
    )

    # FK-индекс (ON DELETE SET NULL без seq-scan)
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_request_wagon_assigned_id
            ON {SCHEMA}.request (wagon_assigned_id)
            WHERE wagon_assigned_id IS NOT NULL
        """
    )

    # Незакрытые заявки без вагона — ядро вычисления requires_assignment
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_request_unassigned
            ON {SCHEMA}.request (status, planned_date)
            WHERE wagon_assigned_id IS NULL
        """
    )

    # Фильтр «Клиент»
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_request_client_name
            ON {SCHEMA}.request (client_name)
        """
    )

    # ------------------------------------------------------------------
    # sync_log: начальные строки (idempotent)
    # ------------------------------------------------------------------
    op.execute(
        f"""
        INSERT INTO {SCHEMA}.sync_log (source, last_status)
        VALUES ('RWL', 'error'), ('1C', 'error')
        ON CONFLICT (source) DO NOTHING
        """
    )

    # CHECK-ограничения на sync_log (могут отсутствовать после 0001)
    op.execute(
        f"""
        ALTER TABLE {SCHEMA}.sync_log
            ADD CONSTRAINT IF NOT EXISTS sync_log_source_check
            CHECK (source IN ('RWL', '1C'))
        """
    )
    op.execute(
        f"""
        ALTER TABLE {SCHEMA}.sync_log
            ADD CONSTRAINT IF NOT EXISTS sync_log_status_check
            CHECK (last_status IN ('success', 'error', 'running'))
        """
    )


def downgrade() -> None:
    # sync_log: убираем CHECK-ограничения
    op.execute(
        f"ALTER TABLE {SCHEMA}.sync_log DROP CONSTRAINT IF EXISTS sync_log_status_check"
    )
    op.execute(
        f"ALTER TABLE {SCHEMA}.sync_log DROP CONSTRAINT IF EXISTS sync_log_source_check"
    )

    # request: откат к исходной схеме 0001
    op.drop_table("request", schema=SCHEMA)

    op.create_table(
        "request",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("wagon_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["wagon_id"],
            [f"{SCHEMA}.wagon.id"],
            name="fk_request_wagon_id_wagon",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_request"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_wagon_service_request_wagon_id", "request", ["wagon_id"], schema=SCHEMA
    )
    op.create_index(
        "ix_wagon_service_request_status", "request", ["status"], schema=SCHEMA
    )

    # wagon: удаляем новые индексы
    for idx in [
        "idx_wagon_sort_default",
        "idx_wagon_requires_assignment",
        "idx_wagon_destination_railway",
        "idx_wagon_supplier_name",
        "idx_wagon_status",
        "idx_wagon_owner_type",
        "idx_wagon_wagon_type",
        "idx_wagon_number_pattern",
        "idx_wagon_destination_station_name_pattern",
        "idx_wagon_assignment_railway",
        "idx_wagon_current_city",
        "idx_wagon_updated_at",
    ]:
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {SCHEMA}.{idx}")

    # wagon: восстанавливаем простые индексы из 0001
    op.create_index(
        "ix_wagon_service_wagon_wagon_type", "wagon", ["wagon_type"], schema=SCHEMA
    )
    op.create_index(
        "ix_wagon_service_wagon_current_station_name",
        "wagon",
        ["current_station_name"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_wagon_service_wagon_current_city", "wagon", ["current_city"], schema=SCHEMA
    )
    op.create_index(
        "ix_wagon_service_wagon_status", "wagon", ["status"], schema=SCHEMA
    )
    op.create_index(
        "ix_wagon_service_wagon_requires_assignment",
        "wagon",
        ["requires_assignment"],
        schema=SCHEMA,
    )

    # wagon: убираем уникальные ограничения
    op.drop_constraint("uq_wagon_number", "wagon", schema=SCHEMA)
    op.drop_constraint("uq_wagon_external_id_rwl", "wagon", schema=SCHEMA)

    # wagon: удаляем новые колонки
    for col in [
        "supplier_name",
        "last_movement_at",
        "days_without_movement",
        "next_destination_station_name",
        "destination_railway",
        "destination_station_name",
    ]:
        op.drop_column("wagon", col, schema=SCHEMA)
