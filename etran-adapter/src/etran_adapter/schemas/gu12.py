from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Gu12CargoItem(BaseModel):
    """Строка с грузом в заявке ГУ-12."""

    etsng_code: str = Field(..., max_length=8, description="Код ЕТСНГ")
    cargo_name: str = Field(..., max_length=255)
    weight_kg: Decimal = Field(..., gt=0)
    container_count: int | None = None


class Gu12WagonItem(BaseModel):
    """Строка с вагоном / типом подвижного состава."""

    wagon_type_code: str = Field(..., max_length=8)
    wagon_count: int = Field(..., gt=0)
    wagon_numbers: list[str] = Field(default_factory=list)

    @field_validator("wagon_numbers")
    @classmethod
    def validate_wagon_number(cls, v: list[str]) -> list[str]:
        for num in v:
            if not num.isdigit() or len(num) != 8:
                raise ValueError(f"Invalid wagon number: {num}")
        return v


class Gu12Request(BaseModel):
    """Заявка ГУ-12 — входные данные для отправки в ЭТРАН."""

    shipper_okpo: str = Field(..., max_length=12, description="ОКПО грузоотправителя")
    shipper_name: str
    departure_station_code: str = Field(..., max_length=8)
    destination_station_code: str = Field(..., max_length=8)
    period_from: date
    period_to: date
    cargo_items: list[Gu12CargoItem] = Field(..., min_length=1)
    wagon_items: list[Gu12WagonItem] = Field(..., min_length=1)
    payer_okpo: str | None = None
    special_conditions: str | None = None


class Gu12Response(BaseModel):
    """Ответ ЭТРАН на запрос создания/подачи ГУ-12."""

    request_id: str
    etran_doc_number: str | None = None
    status_code: str
    status_description: str
    error_code: str | None = None
    error_message: str | None = None
    raw_xml: str | None = None
