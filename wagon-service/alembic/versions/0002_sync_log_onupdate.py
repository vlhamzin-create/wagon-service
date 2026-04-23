"""sync_log: add server-side updated_at trigger for onupdate

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000
"""
from __future__ import annotations

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

SCHEMA = "wagon_service"

# SQL-функция и триггер, которые обеспечивают автоматическое обновление
# updated_at на стороне БД при каждом UPDATE строки в sync_log.
# Это дублирует поведение onupdate=func.now() из ORM-модели и гарантирует
# актуальность поля даже при прямых SQL-запросах в обход ORM.

_CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION {schema}.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;
""".format(schema=SCHEMA)

_DROP_FUNCTION = f"DROP FUNCTION IF EXISTS {SCHEMA}.set_updated_at() CASCADE;"

_CREATE_TRIGGER = f"""
CREATE OR REPLACE TRIGGER trg_sync_log_updated_at
BEFORE UPDATE ON {SCHEMA}.sync_log
FOR EACH ROW EXECUTE FUNCTION {SCHEMA}.set_updated_at();
"""

_DROP_TRIGGER = f"DROP TRIGGER IF EXISTS trg_sync_log_updated_at ON {SCHEMA}.sync_log;"


def upgrade() -> None:
    op.execute(_CREATE_FUNCTION)
    op.execute(_CREATE_TRIGGER)


def downgrade() -> None:
    op.execute(_DROP_TRIGGER)
    op.execute(_DROP_FUNCTION)
