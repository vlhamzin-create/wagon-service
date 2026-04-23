"""Add pg_trgm extension and trigram indexes for ILIKE global search

Revision ID: 0004
Revises: 0003
Create Date: 2024-01-04 00:00:00.000000

Changes
-------
- CREATE EXTENSION IF NOT EXISTS pg_trgm
- GIN-индексы по всем полям глобального поиска (number, destination_railway,
  destination_station_name, next_destination_station_name,
  current_station_name, current_city, supplier_name)
"""
from __future__ import annotations

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"

# Поля, по которым строятся триграмные индексы для ILIKE '%...%'
_TRGM_FIELDS = [
    "number",
    "destination_railway",
    "destination_station_name",
    "next_destination_station_name",
    "current_station_name",
    "current_city",
    "supplier_name",
]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    for field in _TRGM_FIELDS:
        op.execute(
            f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_trgm_{field}
                ON {SCHEMA}.wagon USING GIN ({field} gin_trgm_ops)
                WHERE deleted_at IS NULL
            """
        )


def downgrade() -> None:
    for field in _TRGM_FIELDS:
        op.execute(
            f"DROP INDEX CONCURRENTLY IF EXISTS {SCHEMA}.idx_wagon_trgm_{field}"
        )
