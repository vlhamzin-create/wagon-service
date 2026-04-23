"""add composite indexes for dashboard aggregation

Revision ID: 0010
Revises: 0009
Create Date: 2026-04-23 18:00:00.000000

Changes
-------
- CREATE INDEX idx_wagon_dashboard_category — covering index for the
  dashboard CTE categorization (destination_station_code, distance_to_destination,
  status, wagon_type, owner_type, destination_railway) with deleted_at IS NULL filter.
"""
from __future__ import annotations

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS idx_wagon_dashboard_category
        ON {SCHEMA}.wagon (
            destination_station_code,
            distance_to_destination,
            status,
            wagon_type,
            owner_type,
            destination_railway
        )
        WHERE deleted_at IS NULL
        """
    )


def downgrade() -> None:
    op.execute(
        f"DROP INDEX IF EXISTS {SCHEMA}.idx_wagon_dashboard_category"
    )
