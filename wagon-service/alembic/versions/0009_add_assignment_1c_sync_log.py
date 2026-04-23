"""add assignment_1c_sync_log table and onec_sync columns on wagon

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-23 12:00:00.000000

Changes
-------
- CREATE TABLE assignment_1c_sync_log (лог синхронизации назначений с 1С)
- ALTER TABLE wagon: add onec_sync_status, onec_synced_at
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    # ------------------------------------------------------------------
    # assignment_1c_sync_log
    # ------------------------------------------------------------------
    op.create_table(
        "assignment_1c_sync_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
        sa.Column(
            "attempt_count",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "max_attempts",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("5"),
        ),
        sa.Column("last_attempt_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("next_retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("onec_response_code", sa.SmallInteger(), nullable=True),
        sa.Column("onec_response_body", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=True, unique=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_assignment_1c_sync_log"),
        schema=SCHEMA,
    )

    op.create_index(
        "idx_sync_log_status",
        "assignment_1c_sync_log",
        ["status"],
        schema=SCHEMA,
    )
    op.create_index(
        "idx_sync_log_assignment",
        "assignment_1c_sync_log",
        ["assignment_id"],
        schema=SCHEMA,
    )
    op.execute(
        f"""
        CREATE INDEX idx_sync_log_next_retry
            ON {SCHEMA}.assignment_1c_sync_log (next_retry_at)
            WHERE status IN ('PENDING', 'FAILED')
        """
    )

    # ------------------------------------------------------------------
    # wagon: денормализованный статус синхронизации с 1С
    # ------------------------------------------------------------------
    op.add_column(
        "wagon",
        sa.Column(
            "onec_sync_status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'NOT_SYNCED'"),
        ),
        schema=SCHEMA,
    )
    op.add_column(
        "wagon",
        sa.Column("onec_synced_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_column("wagon", "onec_synced_at", schema=SCHEMA)
    op.drop_column("wagon", "onec_sync_status", schema=SCHEMA)
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_sync_log_next_retry")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_sync_log_assignment")
    op.execute(f"DROP INDEX IF EXISTS {SCHEMA}.idx_sync_log_status")
    op.drop_table("assignment_1c_sync_log", schema=SCHEMA)
