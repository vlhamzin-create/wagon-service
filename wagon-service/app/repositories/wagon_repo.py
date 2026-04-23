from __future__ import annotations

import uuid

from sqlalchemy import asc, desc, func, nulls_last, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request
from app.models.wagon import Wagon
from app.schemas.wagon import FilterOption, FilterOptionsResponse, WagonFilters, WagonFiltersResponse

# Разрешённые поля сортировки — защита от SQL-инъекций через whitelist
SORTABLE_FIELDS: dict[str, object] = {
    "destination_railway": Wagon.destination_railway,
    "destination_station_name": Wagon.destination_station_name,
    "current_city": Wagon.current_city,
    "current_station_name": Wagon.current_station_name,
    "number": Wagon.number,
    "status": Wagon.status,
    "wagon_type": Wagon.wagon_type,
    "owner_type": Wagon.owner_type,
    "supplier_name": Wagon.supplier_name,
    "updated_at": Wagon.updated_at,
}

# Поля, по которым работает глобальный поиск (все отображаемые строковые)
GLOBAL_SEARCH_FIELDS = [
    Wagon.number,
    Wagon.destination_railway,
    Wagon.destination_station_name,
    Wagon.next_destination_station_name,
    Wagon.current_station_name,
    Wagon.current_city,
    Wagon.supplier_name,
]

# Поля для дропдаунов filter-options: имя поля -> (атрибут ORM, label для UI)
_FILTER_OPTION_FIELDS: dict[str, object] = {
    "destination_railway": Wagon.destination_railway,
    "supplier_name": Wagon.supplier_name,
    "current_city": Wagon.current_city,
    "owner_type": Wagon.owner_type,
    "wagon_type": Wagon.wagon_type,
    "status": Wagon.status,
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
        if filters.destination_railway:
            stmt = stmt.where(Wagon.destination_railway.in_(filters.destination_railway))
        if filters.supplier_name:
            stmt = stmt.where(Wagon.supplier_name.in_(filters.supplier_name))
        if filters.current_city:
            stmt = stmt.where(Wagon.current_city.in_(filters.current_city))
        if filters.client_name:
            stmt = stmt.join(
                Request, Request.wagon_assigned_id == Wagon.id,
            ).where(Request.client_name.in_(filters.client_name))
        if filters.current_station_name:
            stmt = stmt.where(Wagon.current_station_name.in_(filters.current_station_name))

        if filters.search and filters.search.strip():
            pattern = f"%{filters.search.strip()}%"
            stmt = stmt.where(
                or_(*(col.ilike(pattern) for col in GLOBAL_SEARCH_FIELDS))
            )

        # TODO-COL-1: days_without_movement вычисляется из last_movement_at,
        # сортировка инвертируется (больше дней = более старый last_movement_at).
        if filters.sort_by == "days_without_movement":
            if filters.sort_dir == "desc":
                sort_expr = nulls_last(asc(Wagon.last_movement_at))
            else:
                sort_expr = nulls_last(desc(Wagon.last_movement_at))
        else:
            sort_col = SORTABLE_FIELDS.get(filters.sort_by, Wagon.destination_railway)
            sort_expr = sort_col.desc() if filters.sort_dir == "desc" else sort_col.asc()
        # Вторичная сортировка: destination_station_name, затем id для стабильной пагинации
        stmt = stmt.order_by(sort_expr, Wagon.destination_station_name.asc(), Wagon.id.asc())

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

    async def get_filters(self) -> WagonFiltersResponse:
        """Возвращает distinct-значения для панели фильтров: дороги, клиенты, поставщики, станции."""
        railways_q = (
            select(Wagon.destination_railway)
            .where(Wagon.deleted_at.is_(None), Wagon.destination_railway.isnot(None))
            .distinct()
            .order_by(Wagon.destination_railway)
        )
        clients_q = (
            select(Request.client_name)
            .join(Wagon, Wagon.id == Request.wagon_assigned_id)
            .where(
                Request.wagon_assigned_id.isnot(None),
                Request.client_name.isnot(None),
                Wagon.deleted_at.is_(None),
            )
            .distinct()
            .order_by(Request.client_name)
        )
        suppliers_q = (
            select(Wagon.supplier_name)
            .where(Wagon.deleted_at.is_(None), Wagon.supplier_name.isnot(None))
            .distinct()
            .order_by(Wagon.supplier_name)
        )
        stations_q = (
            select(Wagon.destination_station_name)
            .where(Wagon.deleted_at.is_(None), Wagon.destination_station_name.isnot(None))
            .distinct()
            .order_by(Wagon.destination_station_name)
        )

        railways_res = (await self._session.execute(railways_q)).scalars().all()
        clients_res = (await self._session.execute(clients_q)).scalars().all()
        suppliers_res = (await self._session.execute(suppliers_q)).scalars().all()
        stations_res = (await self._session.execute(stations_q)).scalars().all()

        return WagonFiltersResponse(
            destination_railways=list(railways_res),
            client_names=list(clients_res),
            suppliers=list(suppliers_res),
            destination_stations=list(stations_res),
        )

    async def get_filter_options(self) -> FilterOptionsResponse:
        """Возвращает уникальные значения для дропдаунов фильтров."""
        result: dict[str, list[FilterOption]] = {}
        for field_name, column in _FILTER_OPTION_FIELDS.items():
            q = (
                select(column)
                .where(Wagon.deleted_at.is_(None), column.isnot(None))
                .distinct()
                .order_by(column)
            )
            values = (await self._session.execute(q)).scalars().all()
            result[field_name] = [FilterOption(value=v, label=v) for v in values]
        return FilterOptionsResponse(**result)
