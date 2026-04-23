"""Add partial index on request.client_name for DISTINCT filter queries

Revision ID: 0014
Revises: 0013
Create Date: 2026-04-24 00:00:00.000000

Changes
-------
- Partial B-Tree index on request.client_name (WHERE client_name IS NOT NULL)
  for efficient DISTINCT in GET /api/v1/wagons/filters → client_names.
- Explicit partial index on request.wagon_assigned_id (WHERE wagon_assigned_id IS NOT NULL)
  already exists in ORM definition; this migration ensures it is present in older environments.
"""
from __future__ import annotations

from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"


def upgrade() -> None:
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_request_client_name_partial
            ON {SCHEMA}.request (client_name)
            WHERE client_name IS NOT NULL
        """
    )
    op.execute(
        f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_request_wagon_assigned_id_partial
            ON {SCHEMA}.request (wagon_assigned_id)
            WHERE wagon_assigned_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute(
        f"DROP INDEX CONCURRENTLY IF EXISTS {SCHEMA}.idx_request_wagon_assigned_id_partial"
    )
    op.execute(
        f"DROP INDEX CONCURRENTLY IF EXISTS {SCHEMA}.idx_request_client_name_partial"
    )
