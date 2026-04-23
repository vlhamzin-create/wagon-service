"""Add NSI ETRAN tables: wagon_type_dict, cargo_dict, nsi_sync_state; extend station_dict

Revision ID: 0012
Revises: 0011
Create Date: 2026-04-24 00:00:00.000000

Changes
-------
- ALTER TABLE station_dict: add short_name, country_code, railway_code, railway_name,
  etran_version, loaded_at, updated_at columns.
- CREATE TABLE wagon_type_dict (справочник типов вагонов из НСИ ЭТРАН).
- CREATE TABLE cargo_dict (справочник грузов ЕТСНГ/ГНГ из НСИ ЭТРАН).
- CREATE TABLE nsi_sync_state (состояние синхронизации справочников).
- GIN trigram indexes for ILIKE autocomplete on cargo_dict.etsng_name.
- Index on cargo_dict.gng_code, station_dict.railway_code.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Extend station_dict with ETRAN-specific columns
    # ------------------------------------------------------------------
    op.add_column(
        "station_dict",
        sa.Column("short_name", sa.String(64), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "station_dict",
        sa.Column("country_code", sa.String(8), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "station_dict",
        sa.Column("railway_code", sa.String(16), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "station_dict",
        sa.Column("railway_name", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "station_dict",
        sa.Column("etran_version", sa.BigInteger(), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "station_dict",
        sa.Column(
            "loaded_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "station_dict",
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_station_dict_railway_code",
        "station_dict",
        ["railway_code"],
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------
    # wagon_type_dict
    # ------------------------------------------------------------------
    op.create_table(
        "wagon_type_dict",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("type_code", sa.String(16), nullable=False),
        sa.Column("type_name", sa.String(255), nullable=False),
        sa.Column("cargo_capacity", sa.Numeric(10, 2), nullable=True),
        sa.Column("volume", sa.Numeric(10, 2), nullable=True),
        sa.Column("tare_weight", sa.Numeric(10, 2), nullable=True),
        sa.Column("axle_count", sa.SmallInteger(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("etran_version", sa.BigInteger(), nullable=True),
        sa.Column(
            "loaded_at",
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
        sa.PrimaryKeyConstraint("id", name="pk_wagon_type_dict"),
        sa.UniqueConstraint("type_code", name="uq_wagon_type_dict_type_code"),
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------
    # cargo_dict
    # ------------------------------------------------------------------
    op.create_table(
        "cargo_dict",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("etsng_code", sa.String(16), nullable=False),
        sa.Column("etsng_name", sa.String(255), nullable=False),
        sa.Column("gng_code", sa.String(16), nullable=True),
        sa.Column("gng_name", sa.String(255), nullable=True),
        sa.Column("cargo_group", sa.String(64), nullable=True),
        sa.Column(
            "is_dangerous",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("etran_version", sa.BigInteger(), nullable=True),
        sa.Column(
            "loaded_at",
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
        sa.PrimaryKeyConstraint("id", name="pk_cargo_dict"),
        sa.UniqueConstraint("etsng_code", name="uq_cargo_dict_etsng_code"),
        schema=SCHEMA,
    )

    op.execute(f"""
        CREATE INDEX IF NOT EXISTS ix_cargo_dict_etsng_name_trgm
            ON {SCHEMA}.cargo_dict USING gin (etsng_name gin_trgm_ops)
    """)
    op.create_index(
        "ix_cargo_dict_gng_code",
        "cargo_dict",
        ["gng_code"],
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------
    # nsi_sync_state
    # ------------------------------------------------------------------
    op.create_table(
        "nsi_sync_state",
        sa.Column("dictionary_name", sa.String(64), nullable=False),
        sa.Column(
            "last_sync_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("last_chg_dt", sa.String(32), nullable=True),
        sa.Column("records_total", sa.Integer(), nullable=True),
        sa.Column("records_upserted", sa.Integer(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            server_default=sa.text("'never_run'"),
        ),
        sa.PrimaryKeyConstraint("dictionary_name", name="pk_nsi_sync_state"),
        sa.CheckConstraint(
            "status IN ('never_run', 'running', 'success', 'error')",
            name="ck_nsi_sync_state_status",
        ),
        schema=SCHEMA,
    )

    op.execute(f"""
        INSERT INTO {SCHEMA}.nsi_sync_state (dictionary_name, status)
        VALUES ('stations', 'never_run'),
               ('wagon_types', 'never_run'),
               ('cargos', 'never_run')
    """)


def downgrade() -> None:
    op.drop_table("nsi_sync_state", schema=SCHEMA)
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.ix_cargo_dict_etsng_name_trgm")
    op.drop_index("ix_cargo_dict_gng_code", table_name="cargo_dict", schema=SCHEMA)
    op.drop_table("cargo_dict", schema=SCHEMA)
    op.drop_table("wagon_type_dict", schema=SCHEMA)
    op.drop_index(
        "ix_station_dict_railway_code",
        table_name="station_dict",
        schema=SCHEMA,
    )
    op.drop_column("station_dict", "updated_at", schema=SCHEMA)
    op.drop_column("station_dict", "loaded_at", schema=SCHEMA)
    op.drop_column("station_dict", "etran_version", schema=SCHEMA)
    op.drop_column("station_dict", "railway_name", schema=SCHEMA)
    op.drop_column("station_dict", "railway_code", schema=SCHEMA)
    op.drop_column("station_dict", "country_code", schema=SCHEMA)
    op.drop_column("station_dict", "short_name", schema=SCHEMA)
