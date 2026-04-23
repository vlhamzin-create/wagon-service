from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wagon_repo import WagonRepository
from app.schemas.wagon import (
    FilterOptionsResponse,
    PaginatedWagons,
    WagonDetail,
    WagonFilters,
    WagonFiltersResponse,
    WagonListItem,
)


class WagonService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = WagonRepository(session)

    async def list_wagons(self, filters: WagonFilters) -> PaginatedWagons:
        items, total = await self._repo.get_list(filters)
        return PaginatedWagons(
            items=[WagonListItem.model_validate(w) for w in items],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
            has_more=(filters.offset + len(items)) < total,
        )

    async def get_wagon(self, wagon_id: uuid.UUID) -> WagonDetail | None:
        wagon = await self._repo.get_by_id(wagon_id)
        if wagon is None:
            return None
        return WagonDetail.model_validate(wagon)

    async def get_filters(self) -> WagonFiltersResponse:
        return await self._repo.get_filters()

    async def get_filter_options(self) -> FilterOptionsResponse:
        return await self._repo.get_filter_options()
