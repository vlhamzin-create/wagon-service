from __future__ import annotations

from pydantic import BaseModel, Field


class RedirectionRequest(BaseModel):
    """Заявление на переадресовку груза."""

    waybill_id: str
    wagon_number: str
    new_destination_station_code: str = Field(..., max_length=8)
    new_destination_station_name: str
    new_consignee_okpo: str | None = None
    new_consignee_name: str | None = None
    reason_code: str = Field(..., description="Код причины переадресовки")
    reason_description: str | None = None


class RedirectionResponse(BaseModel):
    redirection_id: str
    status_code: str
    status_description: str
    approved: bool | None = None
    error_code: str | None = None
    error_message: str | None = None
    raw_xml: str | None = None
