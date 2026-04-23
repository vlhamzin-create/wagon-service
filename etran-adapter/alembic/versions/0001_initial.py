"""Initial schema: request_log table.

Revision ID: 0001
Revises:
Create Date: 2026-04-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "etran_adapter"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "request_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "correlation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("direction", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("request_xml", sa.Text(), nullable=True),
        sa.Column("response_xml", sa.Text(), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("meta", postgresql.JSONB(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_request_log"),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_request_log_correlation_id",
        "request_log",
        ["correlation_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_request_log_operation",
        "request_log",
        ["operation"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("request_log", schema=SCHEMA)
