"""extend wagon table for UC-1.3

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-23 00:00:00.000000

Changes
-------
wagon:
  - ADD COLUMNS: route_station_code, route_station_name,
                 route_client_id (UUID FK -> client_dict),
                 route_client_name,
                 destination_station_code,
                 assigned_destination_delta_distance,
                 assigned_destination_eta,
                 distance_to_destination,
                 waybill_status, sigis_marker, comment
  - ADD FK fk_wagon_route_client_id (DEFERRABLE)
  - ADD INDEXES on route_station_code, route_client_id
  - ADD CHECK ck_wagon_sigis_marker
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # Группа A: поля, назначаемые логистом (UC-1.3 core)
    # ------------------------------------------------------------------ #
    op.add_column(
        "wagon",
        sa.Column("route_station_code", sa.String(16), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("route_station_name", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column(
            "route_client_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("route_client_name", sa.String(255), nullable=True),
        schema=SCHEMA,
    )

    # FK: route_client_id -> client_dict.id
    # Используем deferrable=True чтобы FK не мешал bulk-вставкам НСИ
    op.create_foreign_key(
        constraint_name="fk_wagon_route_client_id",
        source_table="wagon",
        referent_table="client_dict",
        local_cols=["route_client_id"],
        remote_cols=["id"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="SET NULL",
        deferrable=True,
        initially="DEFERRED",
    )

    # Индекс для быстрого поиска вагонов по клиенту/станции
    op.create_index(
        index_name="ix_wagon_route_station_code",
        table_name="wagon",
        columns=["route_station_code"],
        schema=SCHEMA,
    )
    op.create_index(
        index_name="ix_wagon_route_client_id",
        table_name="wagon",
        columns=["route_client_id"],
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------ #
    # Группа B: расчётные и интеграционные поля
    # ------------------------------------------------------------------ #
    op.add_column(
        "wagon",
        sa.Column("destination_station_code", sa.String(16), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column(
            "assigned_destination_delta_distance",
            sa.Numeric(12, 2),
            nullable=True,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("assigned_destination_eta", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column(
            "distance_to_destination",
            sa.Numeric(12, 2),
            nullable=True,
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("waybill_status", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("sigis_marker", sa.String(32), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("comment", sa.Text(), nullable=True),
        schema=SCHEMA,
    )

    # CHECK: допустимые значения sigis_marker
    op.create_check_constraint(
        constraint_name="ck_wagon_sigis_marker",
        table_name="wagon",
        condition="sigis_marker IN ('orange', 'red', 'yellow') OR sigis_marker IS NULL",
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="ck_wagon_sigis_marker",
        table_name="wagon",
        type_="check",
        schema=SCHEMA,
    )
    op.drop_index("ix_wagon_route_client_id", table_name="wagon", schema=SCHEMA)
    op.drop_index("ix_wagon_route_station_code", table_name="wagon", schema=SCHEMA)
    op.drop_constraint(
        constraint_name="fk_wagon_route_client_id",
        table_name="wagon",
        type_="foreignkey",
        schema=SCHEMA,
    )

    cols_to_drop = [
        "route_station_code",
        "route_station_name",
        "route_client_id",
        "route_client_name",
        "destination_station_code",
        "assigned_destination_delta_distance",
        "assigned_destination_eta",
        "distance_to_destination",
        "waybill_status",
        "sigis_marker",
        "comment",
    ]
    for col in cols_to_drop:
        op.drop_column("wagon", col, schema=SCHEMA)
