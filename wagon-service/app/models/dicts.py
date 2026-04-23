from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Integer, Numeric, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SCHEMA


class StationDict(Base):
    __tablename__ = "station_dict"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(64))
    country_code: Mapped[str | None] = mapped_column(String(8))
    country: Mapped[str | None] = mapped_column(String(64))
    railway_code: Mapped[str | None] = mapped_column(String(16))
    railway_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    etran_version: Mapped[int | None] = mapped_column(BigInteger)
    loaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class WagonTypeDict(Base):
    __tablename__ = "wagon_type_dict"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type_code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo_capacity: Mapped[float | None] = mapped_column(Numeric(10, 2))
    volume: Mapped[float | None] = mapped_column(Numeric(10, 2))
    tare_weight: Mapped[float | None] = mapped_column(Numeric(10, 2))
    axle_count: Mapped[int | None] = mapped_column(SmallInteger)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    etran_version: Mapped[int | None] = mapped_column(BigInteger)
    loaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class CargoDict(Base):
    __tablename__ = "cargo_dict"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    etsng_code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    etsng_name: Mapped[str] = mapped_column(String(255), nullable=False)
    gng_code: Mapped[str | None] = mapped_column(String(16))
    gng_name: Mapped[str | None] = mapped_column(String(255))
    cargo_group: Mapped[str | None] = mapped_column(String(64))
    is_dangerous: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    etran_version: Mapped[int | None] = mapped_column(BigInteger)
    loaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class NsiSyncState(Base):
    __tablename__ = "nsi_sync_state"
    __table_args__ = (
        CheckConstraint(
            "status IN ('never_run', 'running', 'success', 'error')",
            name="ck_nsi_sync_state_status",
        ),
        {"schema": SCHEMA},
    )

    dictionary_name: Mapped[str] = mapped_column(
        String(64), primary_key=True
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    last_chg_dt: Mapped[str | None] = mapped_column(String(32))
    records_total: Mapped[int | None] = mapped_column(Integer)
    records_upserted: Mapped[int | None] = mapped_column(Integer)
    last_error: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'never_run'")
    )


class ClientDict(Base):
    __tablename__ = "client_dict"
    __table_args__ = {"schema": SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id_1c: Mapped[str | None] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
