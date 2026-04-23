"""create station_dict and client_dict tables with trgm indexes

Revision ID: 0008
Revises: 0007
Create Date: 2026-04-23 02:00:00.000000

Changes
-------
- CREATE TABLE station_dict (справочник станций)
- CREATE TABLE client_dict (справочник клиентов)
- GIN trigram indexes on station_dict.name, station_dict.code, client_dict.name
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # station_dict
    # ------------------------------------------------------------------
    op.create_table(
        "station_dict",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(16), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country", sa.String(64), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_station_dict"),
        sa.UniqueConstraint("code", name="uq_station_dict_code"),
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------
    # client_dict
    # ------------------------------------------------------------------
    op.create_table(
        "client_dict",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("external_id_1c", sa.String(64), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_client_dict"),
        schema=SCHEMA,
    )

    # ------------------------------------------------------------------
    # Trigram indexes for ILIKE autocomplete
    # ------------------------------------------------------------------
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS ix_station_dict_name_trgm
            ON {SCHEMA}.station_dict USING gin (name gin_trgm_ops)
        """
    )
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS ix_station_dict_code_trgm
            ON {SCHEMA}.station_dict USING gin (code gin_trgm_ops)
        """
    )
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS ix_client_dict_name_trgm
            ON {SCHEMA}.client_dict USING gin (name gin_trgm_ops)
        """
    )


def downgrade() -> None:
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.ix_client_dict_name_trgm")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.ix_station_dict_code_trgm")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.ix_station_dict_name_trgm")
    op.drop_table("client_dict", schema=SCHEMA)
    op.drop_table("station_dict", schema=SCHEMA)
