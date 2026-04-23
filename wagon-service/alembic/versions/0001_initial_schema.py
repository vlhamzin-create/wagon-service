"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "wagon",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id_rwl", sa.String(64), nullable=False),
        sa.Column("number", sa.String(32), nullable=False),
        sa.Column("owner_type", sa.String(32), nullable=False),
        sa.Column("wagon_type", sa.String(32), nullable=False),
        sa.Column("model", sa.String(64), nullable=True),
        sa.Column("capacity_tons", sa.Numeric(10, 2), nullable=True),
        sa.Column("volume_m3", sa.Numeric(10, 2), nullable=True),
        sa.Column("current_country", sa.String(64), nullable=True),
        sa.Column("current_station_code", sa.String(16), nullable=True),
        sa.Column("current_station_name", sa.String(255), nullable=True),
        sa.Column("current_city", sa.String(255), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("requires_assignment", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_wagon"),
        schema=SCHEMA,
    )

    op.create_index("ix_wagon_service_wagon_external_id_rwl", "wagon", ["external_id_rwl"], schema=SCHEMA)
    op.create_index("ix_wagon_service_wagon_number", "wagon", ["number"], schema=SCHEMA)
    op.create_index("ix_wagon_service_wagon_wagon_type", "wagon", ["wagon_type"], schema=SCHEMA)
    op.create_index("ix_wagon_service_wagon_current_station_name", "wagon", ["current_station_name"], schema=SCHEMA)
    op.create_index("ix_wagon_service_wagon_current_city", "wagon", ["current_city"], schema=SCHEMA)
    op.create_index("ix_wagon_service_wagon_status", "wagon", ["status"], schema=SCHEMA)
    op.create_index("ix_wagon_service_wagon_requires_assignment", "wagon", ["requires_assignment"], schema=SCHEMA)

    op.create_table(
        "sync_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.String(16), nullable=False),
        sa.Column("last_success_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(32), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sync_log"),
        sa.UniqueConstraint("source", name="uq_sync_log_source"),
        schema=SCHEMA,
    )

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

    op.create_index("ix_wagon_service_request_wagon_id", "request", ["wagon_id"], schema=SCHEMA)
    op.create_index("ix_wagon_service_request_status", "request", ["status"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_table("request", schema=SCHEMA)
    op.drop_table("sync_log", schema=SCHEMA)
    op.drop_table("wagon", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA}")
