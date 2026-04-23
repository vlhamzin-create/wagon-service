from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCounts(BaseModel):
    under_loading: int
    going_to_loading: int
    under_unloading: int
    going_to_unloading: int
    without_assignment: int
    without_assignment_in_transit: int


class DestinationRailwayRow(CategoryCounts):
    destination_railway: str


class WagonTypeSummaryRow(CategoryCounts):
    wagon_type: str


class OwnerTypeSummaryRow(CategoryCounts):
    owner_type: str


class Totals(BaseModel):
    in_work: int
    requires_assignment: int


class DashboardBasicResponse(BaseModel):
    calculated_at: datetime
    destination_railways: list[DestinationRailwayRow]
    summary_by_wagon_type: list[WagonTypeSummaryRow]
    summary_by_owner_type: list[OwnerTypeSummaryRow]
    totals: Totals
