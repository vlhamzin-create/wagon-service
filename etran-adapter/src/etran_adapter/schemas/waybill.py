from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class WaybillParty(BaseModel):
    okpo: str
    name: str
    inn: str | None = None
    station_code: str
    station_name: str


class WaybillCargo(BaseModel):
    etsng_code: str
    cargo_name: str
    weight_gross_kg: Decimal
    weight_tare_kg: Decimal | None = None
    package_type_code: str | None = None
    package_count: int | None = None


class WaybillWagon(BaseModel):
    wagon_number: str
    wagon_type: str
    load_capacity_t: Decimal | None = None
    tare_weight_t: Decimal | None = None


class WaybillRequest(BaseModel):
    """Накладная для подачи на визирование или на погрузку."""

    operation_type: Literal["visaRequest", "loadRequest"]
    shipper: WaybillParty
    consignee: WaybillParty
    cargo: WaybillCargo
    wagons: list[WaybillWagon] = Field(..., min_length=1)
    departure_date: datetime | None = None
    gu12_id: str | None = None
    special_marks: str | None = None


class WaybillResponse(BaseModel):
    waybill_id: str
    waybill_number: str | None = None
    visa_status: str | None = None
    status_code: str
    status_description: str
    error_code: str | None = None
    error_message: str | None = None
    raw_xml: str | None = None
