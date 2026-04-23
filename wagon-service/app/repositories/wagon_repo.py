from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wagon import Wagon
from app.schemas.wagon import WagonFilters

# Разрешённые поля сортировки — защита от SQL-инъекций
SORTABLE_FIELDS: dict[str, object] = {
    "current_city": Wagon.current_city,
    "current_station_name": Wagon.current_station_name,
    "number": Wagon.number,
    "status": Wagon.status,
    "wagon_type": Wagon.wagon_type,
    "owner_type": Wagon.owner_type,
    "updated_at": Wagon.updated_at,
}


class WagonRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _build_query(self, filters: WagonFilters):
        stmt = select(Wagon).where(Wagon.deleted_at.is_(None))

        if filters.mode == "requires_assignment":
            stmt = stmt.where(Wagon.requires_assignment.is_(True))

        if filters.owner_type:
            stmt = stmt.where(Wagon.owner_type.in_(filters.owner_type))
        if filters.wagon_type:
            stmt = stmt.where(Wagon.wagon_type.in_(filters.wagon_type))
        if filters.status:
            stmt = stmt.where(Wagon.status.in_(filters.status))
        if filters.current_city:
            stmt = stmt.where(Wagon.current_city.in_(filters.current_city))
        if filters.current_station_name:
            stmt = stmt.where(Wagon.current_station_name.in_(filters.current_station_name))

        if filters.search:
            pattern = f"%{filters.search}%"
            stmt = stmt.where(
                or_(
                    Wagon.number.ilike(pattern),
                    Wagon.current_station_name.ilike(pattern),
                    Wagon.current_city.ilike(pattern),
                    Wagon.status.ilike(pattern),
                )
            )

        sort_col = SORTABLE_FIELDS.get(filters.sort_by, Wagon.current_city)
        sort_expr = sort_col.desc() if filters.sort_dir == "desc" else sort_col.asc()
        stmt = stmt.order_by(sort_expr, Wagon.current_station_name.asc(), Wagon.id.asc())

        return stmt

    async def get_list(self, filters: WagonFilters) -> tuple[list[Wagon], int]:
        base_stmt = self._build_query(filters)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total: int = (await self._session.execute(count_stmt)).scalar_one()

        data_stmt = base_stmt.limit(filters.limit).offset(filters.offset)
        result = await self._session.execute(data_stmt)
        items = list(result.scalars().all())

        return items, total

    async def get_by_id(self, wagon_id: uuid.UUID) -> Wagon | None:
        stmt = select(Wagon).where(Wagon.id == wagon_id, Wagon.deleted_at.is_(None))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
