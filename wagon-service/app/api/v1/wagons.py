from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TokenPayload
from app.dependencies import get_db, require_any_role
from app.schemas.wagon import FilterOptionsResponse, PaginatedWagons, WagonDetail, WagonFilters, WagonFiltersResponse
from app.services.wagon_service import WagonService

router = APIRouter(prefix="/wagons", tags=["wagons"])


# ВАЖНО: /filters и /filter-options должны быть зарегистрированы ДО /{wagon_id},
# иначе FastAPI матчит строку как wagon_id (UUID) и падает с 422.
@router.get(
    "/filters",
    response_model=WagonFiltersResponse,
    summary="Distinct-значения для панели фильтров: дороги, клиенты, поставщики, станции",
)
async def get_filters(
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(require_any_role),
) -> WagonFiltersResponse:
    return await WagonService(db).get_filters()


@router.get(
    "/filter-options",
    response_model=FilterOptionsResponse,
    summary="Уникальные значения для дропдаунов фильтров",
)
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(require_any_role),
) -> FilterOptionsResponse:
    return await WagonService(db).get_filter_options()


@router.get("", response_model=PaginatedWagons, summary="Список вагонов с фильтрацией и пагинацией")
async def list_wagons(
    # Пагинация
    limit: Annotated[int, Query(ge=1, le=100, description="Размер страницы")] = 100,
    offset: Annotated[int, Query(ge=0, description="Смещение")] = 0,
    # Режим
    mode: Annotated[str, Query(description="all | requires_assignment")] = "all",
    # Фильтры-списки (повторяющиеся query-параметры)
    owner_type: Annotated[list[str] | None, Query()] = None,
    wagon_type: Annotated[list[str] | None, Query()] = None,
    status_filter: Annotated[list[str] | None, Query(alias="status")] = None,
    destination_railway: Annotated[list[str] | None, Query(description="Фильтр по дороге назначения")] = None,
    supplier_name: Annotated[list[str] | None, Query(description="Фильтр по поставщику")] = None,
    client_name: Annotated[
        list[str] | None,
        Query(alias="filter[client_name]", description="Фильтр по клиенту (repeated params)"),
    ] = None,
    current_city: Annotated[list[str] | None, Query()] = None,
    current_station_name: Annotated[list[str] | None, Query()] = None,
    # Поиск и сортировка
    search: Annotated[str | None, Query(max_length=200)] = None,
    sort_by: Annotated[str, Query(description="Поле сортировки")] = "destination_railway",
    sort_dir: Annotated[str, Query(description="asc | desc")] = "desc",
    # Зависимости
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(require_any_role),
) -> PaginatedWagons:
    filters = WagonFilters(
        mode=mode,  # type: ignore[arg-type]
        owner_type=owner_type,
        wagon_type=wagon_type,
        status=status_filter,
        destination_railway=destination_railway,
        supplier_name=supplier_name,
        client_name=client_name,
        current_city=current_city,
        current_station_name=current_station_name,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,  # type: ignore[arg-type]
        limit=limit,
        offset=offset,
    )
    return await WagonService(db).list_wagons(filters)


@router.get("/{wagon_id}", response_model=WagonDetail, summary="Детальная карточка вагона")
async def get_wagon(
    wagon_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(require_any_role),
) -> WagonDetail:
    wagon = await WagonService(db).get_wagon(wagon_id)
    if wagon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wagon not found")
    return wagon
