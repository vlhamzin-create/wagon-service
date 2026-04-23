"""Add indexes for DISTINCT filter queries on destination_station_name

Revision ID: 0005
Revises: 0004
Create Date: 2024-01-05 00:00:00.000000

Changes
-------
- B-Tree index on wagon.destination_station_name (partial, deleted_at IS NULL)
  for efficient DISTINCT in GET /api/v1/wagons/filters
"""
from __future__ import annotations

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_wagon_destination_station_name
            ON {SCHEMA}.wagon (destination_station_name)
            WHERE deleted_at IS NULL
        """
    )


def downgrade() -> None:
    op.execute(
        f"DROP INDEX CONCURRENTLY IF EXISTS {SCHEMA}.idx_wagon_destination_station_name"
    )
