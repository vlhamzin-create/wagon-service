"""ETRAN document storage schema: document_type_dict, message_exchange,
document, document_status_history, operation_request.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

SCHEMA = "etran_adapter"


def upgrade() -> None:
    # -- document_type_dict --------------------------------------------------
    op.create_table(
        "document_type_dict",
        sa.Column("id", sa.SmallInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("api_section", sa.String(32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_type_dict"),
        sa.UniqueConstraint("code", name="uq_document_type_dict_code"),
        schema=SCHEMA,
    )

    # Seed data
    op.execute(
        f"""
        INSERT INTO {SCHEMA}.document_type_dict (code, name, category, api_section) VALUES
            ('GU12',          'Заявка на перевозку грузов ГУ-12',         'APPLICATION', '5.2'),
            ('WAYBILL',       'Накладная',                                 'WAYBILL',     '5.3'),
            ('WAYBILL_EMPTY', 'Накладная на возврат порожняка',            'WAYBILL',     '5.3'),
            ('REDIRECT',      'Заявление на переадресовку',                'APPLICATION', '5.11'),
            ('VPU',           'Ведомость подачи-уборки вагонов',           'ACT',         '5.8'),
            ('VUK',           'Ведомость учёта времени нахождения конт.',  'ACT',         '5.9'),
            ('ACT_GU22',      'Акт общей формы ГУ-22',                    'ACT',         '5.10'),
            ('ACT_GU23',      'Коммерческий акт ГУ-23',                   'ACT',         '5.10'),
            ('KKR',           'Карточка контроля расчёта',                 'FINANCE',     '5.4'),
            ('INVOICE',       'Счёт-фактура',                              'FINANCE',     '5.18'),
            ('ASOUP_REF',     'Информационная справка АСОУП',              'REFERENCE',   '5.28')
        """
    )

    # -- message_exchange ----------------------------------------------------
    op.create_table(
        "message_exchange",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("direction", sa.String(16), nullable=False),
        sa.Column("processing_status", sa.String(32), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("api_method", sa.String(16), nullable=False),
        sa.Column("operation_code", sa.String(64), nullable=True),
        sa.Column("document_type_code", sa.String(64), nullable=True),
        sa.Column("etran_doc_id", sa.String(64), nullable=True),
        sa.Column("wagon_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("raw_xml", sa.Text(), nullable=False),
        sa.Column("parsed_attributes", postgresql.JSONB(), nullable=True),
        sa.Column("error_details", postgresql.JSONB(), nullable=True),
        sa.Column("has_signature", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("signature_version", sa.SmallInteger(), nullable=True),
        sa.Column("signature_verified", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("processed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_system", sa.String(64), nullable=False, server_default=sa.text("'wagon-service'")),
        sa.PrimaryKeyConstraint("id", name="pk_message_exchange"),
        sa.ForeignKeyConstraint(
            ["document_type_code"],
            [f"{SCHEMA}.document_type_dict.code"],
            name="fk_message_exchange_document_type_code_document_type_dict",
        ),
        sa.ForeignKeyConstraint(
            ["related_message_id"],
            [f"{SCHEMA}.message_exchange.id"],
            name="fk_message_exchange_related_message_id_message_exchange",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_message_exchange_created_at",
        "message_exchange",
        ["created_at"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_message_exchange_direction",
        "message_exchange",
        ["direction"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_message_exchange_processing_status",
        "message_exchange",
        ["processing_status"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_message_exchange_etran_doc_id",
        "message_exchange",
        ["etran_doc_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_message_exchange_parsed_attributes",
        "message_exchange",
        ["parsed_attributes"],
        schema=SCHEMA,
        postgresql_using="gin",
    )

    # -- document ------------------------------------------------------------
    op.create_table(
        "document",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("document_type_code", sa.String(64), nullable=False),
        sa.Column("etran_id", sa.String(64), nullable=True),
        sa.Column("etran_number", sa.String(64), nullable=True),
        sa.Column("parent_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("current_status", sa.String(32), nullable=False, server_default=sa.text("'DRAFT'")),
        sa.Column("etran_status_raw", sa.String(64), nullable=True),
        sa.Column("wagon_number", sa.String(10), nullable=True),
        sa.Column("container_number", sa.String(16), nullable=True),
        sa.Column("cargo_code", sa.String(10), nullable=True),
        sa.Column("sender_station_code", sa.String(8), nullable=True),
        sa.Column("dest_station_code", sa.String(8), nullable=True),
        sa.Column("shipper_okpo", sa.String(16), nullable=True),
        sa.Column("consignee_okpo", sa.String(16), nullable=True),
        sa.Column("wagon_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("route_client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("initial_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("last_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requires_signature", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("signed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("signed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.PrimaryKeyConstraint("id", name="pk_document"),
        sa.UniqueConstraint("etran_id", name="uq_document_etran_id"),
        sa.ForeignKeyConstraint(
            ["document_type_code"],
            [f"{SCHEMA}.document_type_dict.code"],
            name="fk_document_document_type_code_document_type_dict",
        ),
        sa.ForeignKeyConstraint(
            ["parent_document_id"],
            [f"{SCHEMA}.document.id"],
            name="fk_document_parent_document_id_document",
        ),
        sa.ForeignKeyConstraint(
            ["initial_message_id"],
            [f"{SCHEMA}.message_exchange.id"],
            name="fk_document_initial_message_id_message_exchange",
        ),
        sa.ForeignKeyConstraint(
            ["last_message_id"],
            [f"{SCHEMA}.message_exchange.id"],
            name="fk_document_last_message_id_message_exchange",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_document_etran_id", "document", ["etran_id"], schema=SCHEMA)
    op.create_index("ix_document_wagon_id", "document", ["wagon_id"], schema=SCHEMA)
    op.create_index(
        "ix_document_type_status",
        "document",
        ["document_type_code", "current_status"],
        schema=SCHEMA,
    )
    op.create_index("ix_document_wagon_number", "document", ["wagon_number"], schema=SCHEMA)
    op.create_index(
        "ix_document_created_at",
        "document",
        [sa.text("created_at DESC")],
        schema=SCHEMA,
    )

    # -- document_status_history ---------------------------------------------
    op.create_table(
        "document_status_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status_from", sa.String(32), nullable=True),
        sa.Column("status_to", sa.String(32), nullable=False),
        sa.Column("etran_status_raw", sa.String(64), nullable=True),
        sa.Column("triggered_by", sa.String(32), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "occurred_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_status_history"),
        sa.ForeignKeyConstraint(
            ["document_id"],
            [f"{SCHEMA}.document.id"],
            name="fk_document_status_history_document_id_document",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            [f"{SCHEMA}.message_exchange.id"],
            name="fk_document_status_history_message_id_message_exchange",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_document_status_history_document_id",
        "document_status_history",
        ["document_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_document_status_history_occurred_at",
        "document_status_history",
        ["occurred_at"],
        schema=SCHEMA,
    )

    # -- operation_request ---------------------------------------------------
    op.create_table(
        "operation_request",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operation_code", sa.String(64), nullable=False),
        sa.Column("api_method", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("request_params", postgresql.JSONB(), nullable=True),
        sa.Column("response_summary", postgresql.JSONB(), nullable=True),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("next_retry_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_operation_request"),
        sa.ForeignKeyConstraint(
            ["document_id"],
            [f"{SCHEMA}.document.id"],
            name="fk_operation_request_document_id_document",
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            [f"{SCHEMA}.message_exchange.id"],
            name="fk_operation_request_message_id_message_exchange",
        ),
        schema=SCHEMA,
    )
    op.create_index(
        "ix_operation_request_document_id",
        "operation_request",
        ["document_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "ix_operation_request_status",
        "operation_request",
        ["status"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("operation_request", schema=SCHEMA)
    op.drop_table("document_status_history", schema=SCHEMA)
    op.drop_table("document", schema=SCHEMA)
    op.drop_table("message_exchange", schema=SCHEMA)
    op.drop_table("document_type_dict", schema=SCHEMA)
