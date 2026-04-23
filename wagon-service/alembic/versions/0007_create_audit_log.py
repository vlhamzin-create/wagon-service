"""create audit_log table

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-23 01:00:00.000000

Changes
-------
- CREATE TABLE audit_log (append-only журнал изменений)
  PK: BIGSERIAL (монотонный, эффективен для append-only)
  JSONB: changes, context
- ADD INDEXES: entity(type+id+time), user+time, GIN on changes
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    op.create_table(
        "audit_log",
        # PK: bigserial — монотонный, эффективен для append-only журнала
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(always=False),
            primary_key=True,
        ),
        # Время события — с timezone, всегда UTC на уровне приложения
        sa.Column(
            "event_time",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        # Пользователь из JWT-токена (без FK — auth живёт в отдельном сервисе)
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Тип сущности: 'wagon', 'request', 'filter_preset', ...
        sa.Column("entity_type", sa.String(64), nullable=False),
        # ID сущности (wagon.id, request.id, ...)
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Код действия: 'assign_route', 'update_status', 'create_request', ...
        sa.Column("action", sa.String(64), nullable=False),
        # Контекст операции: {"bulk": true, "count": 5, "request_id": "..."}
        sa.Column(
            "context",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        # Изменения: {"route_station_code": {"old": "100500", "new": "200600"}, ...}
        sa.Column(
            "changes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        # Источник: 'ui', 'api', 'integration', 'system'
        sa.Column("source", sa.String(64), nullable=True),
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------ #
    # Индексы
    # ------------------------------------------------------------------ #

    # Основной поисковый паттерн: история изменений конкретной сущности
    op.create_index(
        index_name="ix_audit_log_entity",
        table_name="audit_log",
        columns=["entity_type", "entity_id", "event_time"],
        schema=SCHEMA,
    )

    # Поиск по пользователю + время (журнал действий пользователя)
    op.create_index(
        index_name="ix_audit_log_user_time",
        table_name="audit_log",
        columns=["user_id", "event_time"],
        schema=SCHEMA,
    )

    # GIN-индекс на changes для запросов типа:
    # WHERE changes ? 'route_station_code'
    # WHERE changes @> '{"route_station_code": {"new": "200600"}}'
    op.create_index(
        index_name="ix_audit_log_changes_gin",
        table_name="audit_log",
        columns=["changes"],
        schema=SCHEMA,
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_audit_log_changes_gin", table_name="audit_log", schema=SCHEMA)
    op.drop_index("ix_audit_log_user_time", table_name="audit_log", schema=SCHEMA)
    op.drop_index("ix_audit_log_entity", table_name="audit_log", schema=SCHEMA)
    op.drop_table("audit_log", schema=SCHEMA)
