import uuid
from datetime import datetime

from sqlalchemy import Boolean, Numeric, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Wagon(Base):
    __tablename__ = "wagon"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id_rwl: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    owner_type: Mapped[str] = mapped_column(String(32), nullable=False)
    wagon_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    model: Mapped[str | None] = mapped_column(String(64))
    capacity_tons: Mapped[float | None] = mapped_column(Numeric(10, 2))
    volume_m3: Mapped[float | None] = mapped_column(Numeric(10, 2))
    current_country: Mapped[str | None] = mapped_column(String(64))
    current_station_code: Mapped[str | None] = mapped_column(String(16))
    current_station_name: Mapped[str | None] = mapped_column(String(255), index=True)
    current_city: Mapped[str | None] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    requires_assignment: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
