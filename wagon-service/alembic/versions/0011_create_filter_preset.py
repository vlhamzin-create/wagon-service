"""create filter_preset table

Revision ID: 0011
Revises: 0010
Create Date: 2026-04-23 00:00:00.000000

Changes
-------
- CREATE TABLE filter_preset with id, user_id, scope, name, description, filters (JSONB),
  created_at, updated_at.
- Composite index on (user_id, scope) for fast lookups.
- Trigger for auto-updating updated_at on row modification.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    op.create_table(
        "filter_preset",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("scope", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("filters", JSONB, nullable=False),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        schema=SCHEMA,
    )

    op.create_index(
        "ix_filter_preset_user_id_scope",
        "filter_preset",
        ["user_id", "scope"],
        schema=SCHEMA,
    )

    op.execute(f"""
        CREATE OR REPLACE FUNCTION {SCHEMA}.set_filter_preset_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute(f"""
        CREATE TRIGGER trg_filter_preset_updated_at
        BEFORE UPDATE ON {SCHEMA}.filter_preset
        FOR EACH ROW EXECUTE FUNCTION {SCHEMA}.set_filter_preset_updated_at();
    """)


def downgrade() -> None:
    op.execute(
        f"DROP TRIGGER IF EXISTS trg_filter_preset_updated_at "
        f"ON {SCHEMA}.filter_preset;"
    )
    op.drop_index(
        "ix_filter_preset_user_id_scope",
        table_name="filter_preset",
        schema=SCHEMA,
    )
    op.drop_table("filter_preset", schema=SCHEMA)
    op.execute(
        f"DROP FUNCTION IF EXISTS {SCHEMA}.set_filter_preset_updated_at();"
    )
