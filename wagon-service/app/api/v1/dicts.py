from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import TokenPayload
from app.dependencies import get_db, require_any_role
from app.models.dicts import ClientDict, StationDict
from app.schemas.clients import ClientItem, ClientsResponse
from app.schemas.stations import StationItem, StationsResponse

router = APIRouter(tags=["dictionaries"])


@router.get("/stations", response_model=StationsResponse, summary="Справочник станций (автокомплит)")
async def get_stations(
    q: Annotated[str | None, Query(max_length=200, description="Поиск по коду или названию")] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(require_any_role),
) -> StationsResponse:
    stmt = select(StationDict).where(StationDict.is_active.is_(True))

    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                StationDict.name.ilike(pattern),
                StationDict.code.ilike(pattern),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(StationDict.name).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()

    return StationsResponse(
        items=[StationItem.model_validate(r) for r in rows],
        total=total,
    )


@router.get("/clients", response_model=ClientsResponse, summary="Справочник клиентов (автокомплит)")
async def get_clients(
    q: Annotated[str | None, Query(max_length=200, description="Поиск по названию")] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(require_any_role),
) -> ClientsResponse:
    stmt = select(ClientDict).where(ClientDict.is_active.is_(True))

    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(ClientDict.name.ilike(pattern))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(ClientDict.name).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()

    return ClientsResponse(
        items=[ClientItem.model_validate(r) for r in rows],
        total=total,
    )
