from __future__ import annotations

import asyncio
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dicts import ClientDict, StationDict
from app.models.wagon import Wagon
from app.schemas.assign_route import (
    AssignRouteRequest,
    AssignRouteResponse,
    WagonAssignResult,
)
from app.services.audit import write_audit_entries
from app.services.onec_assignment_service import OneCAssignmentService

log = structlog.get_logger(__name__)


class AssignRouteService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._onec_service = OneCAssignmentService(session)

    async def assign(
        self,
        req: AssignRouteRequest,
        user_id: uuid.UUID,
    ) -> AssignRouteResponse:
        # Resolve station from dict
        station = None
        if req.station_code is not None:
            stmt = select(StationDict).where(
                StationDict.code == req.station_code,
                StationDict.is_active.is_(True),
            )
            station = (await self._session.execute(stmt)).scalar_one_or_none()
            if station is None:
                return self._all_error(
                    req.wagon_ids, f"Станция с кодом {req.station_code} не найдена"
                )

        # Resolve client from dict
        client = None
        if req.client_id is not None:
            stmt = select(ClientDict).where(
                ClientDict.id == req.client_id,
                ClientDict.is_active.is_(True),
            )
            client = (await self._session.execute(stmt)).scalar_one_or_none()
            if client is None:
                return self._all_error(
                    req.wagon_ids, f"Клиент с id {req.client_id} не найден"
                )

        # Load wagons
        stmt = select(Wagon).where(
            Wagon.id.in_(req.wagon_ids),
            Wagon.deleted_at.is_(None),
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        found_map: dict[uuid.UUID, Wagon] = {w.id: w for w in rows}

        results: list[WagonAssignResult] = []
        updated_ids: list[uuid.UUID] = []
        changes: dict = {}

        for wid in req.wagon_ids:
            wagon = found_map.get(wid)
            if wagon is None:
                results.append(
                    WagonAssignResult(wagon_id=wid, status="error", reason="Вагон не найден")
                )
                continue

            # Check overwrite
            has_station = wagon.route_station_code is not None
            has_client = wagon.route_client_id is not None
            if not req.overwrite and (
                (station is not None and has_station)
                or (client is not None and has_client)
            ):
                results.append(
                    WagonAssignResult(
                        wagon_id=wid,
                        status="skipped",
                        reason="Маршрут уже назначен, overwrite=false",
                    )
                )
                continue

            # Apply changes
            entry_changes: dict = {}
            if station is not None:
                entry_changes["route_station_code"] = {
                    "old": wagon.route_station_code,
                    "new": station.code,
                }
                entry_changes["route_station_name"] = {
                    "old": wagon.route_station_name,
                    "new": station.name,
                }
                wagon.route_station_code = station.code
                wagon.route_station_name = station.name

            if client is not None:
                entry_changes["route_client_id"] = {
                    "old": str(wagon.route_client_id) if wagon.route_client_id else None,
                    "new": str(client.id),
                }
                entry_changes["route_client_name"] = {
                    "old": wagon.route_client_name,
                    "new": client.name,
                }
                wagon.route_client_id = client.id
                wagon.route_client_name = client.name

            if not changes:
                changes = entry_changes

            updated_ids.append(wid)
            results.append(WagonAssignResult(wagon_id=wid, status="ok"))

        # Write audit + flush in single transaction
        if updated_ids:
            await write_audit_entries(
                self._session,
                user_id=user_id,
                wagon_ids=updated_ids,
                action="assign_route",
                changes=changes,
                context={
                    "bulk": len(updated_ids) > 1,
                    "count": len(updated_ids),
                    "station_code": req.station_code,
                    "client_id": str(req.client_id) if req.client_id else None,
                    "overwrite": req.overwrite,
                },
            )

            # Создаём запись для синхронизации с 1С (assignment_id = batch UUID)
            batch_id = uuid.uuid4()
            sync_entry = await self._onec_service.create_sync_entry(batch_id)

            await self._session.commit()

            # Отправку в 1С запускаем в фоне, не блокируя HTTP-ответ
            client_ext_id: str | None = None
            if client is not None:
                client_ext_id = client.external_id_1c

            asyncio.create_task(
                self._send_to_1c_background(
                    sync_entry=sync_entry,
                    wagon_ids=updated_ids,
                    station_code=req.station_code,
                    client_external_id=client_ext_id,
                    user_id=user_id,
                )
            )

        succeeded = sum(1 for r in results if r.status == "ok")
        skipped = sum(1 for r in results if r.status == "skipped")
        failed = sum(1 for r in results if r.status == "error")

        return AssignRouteResponse(
            total=len(req.wagon_ids),
            succeeded=succeeded,
            skipped=skipped,
            failed=failed,
            results=results,
        )

    async def _send_to_1c_background(
        self,
        sync_entry,
        wagon_ids: list[uuid.UUID],
        station_code: str | None,
        client_external_id: str | None,
        user_id: uuid.UUID,
    ) -> None:
        """Фоновая отправка назначения в 1С. Ошибки логируются, не пробрасываются."""
        try:
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as bg_session:
                service = OneCAssignmentService(bg_session)
                # Загружаем sync_entry заново в новой сессии
                repo = service._repo
                entry = await repo.get_by_assignment(sync_entry.assignment_id)
                if entry is None:
                    log.error(
                        "onec_bg.entry_not_found",
                        assignment_id=str(sync_entry.assignment_id),
                    )
                    return
                await service.send_to_1c(
                    sync_log=entry,
                    wagon_ids=wagon_ids,
                    station_code=station_code,
                    client_external_id=client_external_id,
                    user_id=user_id,
                )
        except Exception:
            log.exception(
                "onec_bg.send_failed",
                assignment_id=str(sync_entry.assignment_id),
            )

    @staticmethod
    def _all_error(wagon_ids: list[uuid.UUID], reason: str) -> AssignRouteResponse:
        results = [
            WagonAssignResult(wagon_id=wid, status="error", reason=reason)
            for wid in wagon_ids
        ]
        return AssignRouteResponse(
            total=len(wagon_ids),
            succeeded=0,
            skipped=0,
            failed=len(wagon_ids),
            results=results,
        )
