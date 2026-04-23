"""Unit-тесты для POST /assign-route."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.assign_route import AssignRouteRequest, AssignRouteResponse
from app.services.assign_route import AssignRouteService


def _make_station(code: str = "060005", name: str = "Москва-Товарная"):
    s = MagicMock()
    s.code = code
    s.name = name
    s.is_active = True
    return s


def _make_client(client_id: uuid.UUID | None = None, name: str = "ООО Ромашка"):
    c = MagicMock()
    c.id = client_id or uuid.uuid4()
    c.name = name
    c.is_active = True
    return c


def _make_wagon(wagon_id: uuid.UUID | None = None, has_route: bool = False):
    w = MagicMock()
    w.id = wagon_id or uuid.uuid4()
    w.route_station_code = "999999" if has_route else None
    w.route_station_name = "Existing" if has_route else None
    w.route_client_id = uuid.uuid4() if has_route else None
    w.route_client_name = "Old Client" if has_route else None
    w.deleted_at = None
    return w


# ---------------------------------------------------------------------------
# Валидация Pydantic
# ---------------------------------------------------------------------------


def test_request_rejects_empty_wagon_ids():
    with pytest.raises(ValueError, match="wagon_ids"):
        AssignRouteRequest(wagon_ids=[], station_code="001")


def test_request_rejects_no_target():
    with pytest.raises(ValueError, match="station_code или client_id"):
        AssignRouteRequest(wagon_ids=[uuid.uuid4()])


def test_request_rejects_over_200():
    with pytest.raises(ValueError, match="200"):
        AssignRouteRequest(
            wagon_ids=[uuid.uuid4() for _ in range(201)],
            station_code="001",
        )


def test_request_valid_with_station():
    req = AssignRouteRequest(wagon_ids=[uuid.uuid4()], station_code="001")
    assert req.station_code == "001"


def test_request_valid_with_client():
    cid = uuid.uuid4()
    req = AssignRouteRequest(wagon_ids=[uuid.uuid4()], client_id=cid)
    assert req.client_id == cid


# ---------------------------------------------------------------------------
# Сервис: назначение маршрута
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_assign_route_success():
    session = AsyncMock()
    service = AssignRouteService(session)

    wagon_id = uuid.uuid4()
    wagon = _make_wagon(wagon_id)
    station = _make_station()

    # Mock execute calls: station lookup, then wagon lookup
    station_result = MagicMock()
    station_result.scalar_one_or_none.return_value = station

    wagon_result_scalars = MagicMock()
    wagon_result_scalars.all.return_value = [wagon]
    wagon_result = MagicMock()
    wagon_result.scalars.return_value = wagon_result_scalars

    session.execute = AsyncMock(side_effect=[station_result, wagon_result])
    session.commit = AsyncMock()

    req = AssignRouteRequest(wagon_ids=[wagon_id], station_code="060005")
    user_id = uuid.uuid4()

    with patch("app.services.assign_route.write_audit_entries", new=AsyncMock()) as mock_audit:
        resp = await service.assign(req, user_id=user_id)

    assert isinstance(resp, AssignRouteResponse)
    assert resp.succeeded == 1
    assert resp.skipped == 0
    assert resp.failed == 0
    assert resp.results[0].status == "ok"
    mock_audit.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_assign_route_skipped_without_overwrite():
    session = AsyncMock()
    service = AssignRouteService(session)

    wagon_id = uuid.uuid4()
    wagon = _make_wagon(wagon_id, has_route=True)
    station = _make_station()

    station_result = MagicMock()
    station_result.scalar_one_or_none.return_value = station

    wagon_result_scalars = MagicMock()
    wagon_result_scalars.all.return_value = [wagon]
    wagon_result = MagicMock()
    wagon_result.scalars.return_value = wagon_result_scalars

    session.execute = AsyncMock(side_effect=[station_result, wagon_result])

    req = AssignRouteRequest(
        wagon_ids=[wagon_id], station_code="060005", overwrite=False
    )

    resp = await service.assign(req, user_id=uuid.uuid4())

    assert resp.skipped == 1
    assert resp.succeeded == 0
    assert resp.results[0].status == "skipped"


@pytest.mark.asyncio
async def test_assign_route_overwrite():
    session = AsyncMock()
    service = AssignRouteService(session)

    wagon_id = uuid.uuid4()
    wagon = _make_wagon(wagon_id, has_route=True)
    station = _make_station()

    station_result = MagicMock()
    station_result.scalar_one_or_none.return_value = station

    wagon_result_scalars = MagicMock()
    wagon_result_scalars.all.return_value = [wagon]
    wagon_result = MagicMock()
    wagon_result.scalars.return_value = wagon_result_scalars

    session.execute = AsyncMock(side_effect=[station_result, wagon_result])
    session.commit = AsyncMock()

    req = AssignRouteRequest(
        wagon_ids=[wagon_id], station_code="060005", overwrite=True
    )

    with patch("app.services.assign_route.write_audit_entries", new=AsyncMock()):
        resp = await service.assign(req, user_id=uuid.uuid4())

    assert resp.succeeded == 1
    assert resp.results[0].status == "ok"


@pytest.mark.asyncio
async def test_assign_route_wagon_not_found():
    session = AsyncMock()
    service = AssignRouteService(session)

    wagon_id = uuid.uuid4()
    station = _make_station()

    station_result = MagicMock()
    station_result.scalar_one_or_none.return_value = station

    wagon_result_scalars = MagicMock()
    wagon_result_scalars.all.return_value = []
    wagon_result = MagicMock()
    wagon_result.scalars.return_value = wagon_result_scalars

    session.execute = AsyncMock(side_effect=[station_result, wagon_result])

    req = AssignRouteRequest(wagon_ids=[wagon_id], station_code="060005")
    resp = await service.assign(req, user_id=uuid.uuid4())

    assert resp.failed == 1
    assert resp.results[0].status == "error"
    assert "не найден" in resp.results[0].reason


@pytest.mark.asyncio
async def test_assign_route_station_not_found():
    session = AsyncMock()
    service = AssignRouteService(session)

    station_result = MagicMock()
    station_result.scalar_one_or_none.return_value = None

    session.execute = AsyncMock(return_value=station_result)

    wagon_id = uuid.uuid4()
    req = AssignRouteRequest(wagon_ids=[wagon_id], station_code="INVALID")
    resp = await service.assign(req, user_id=uuid.uuid4())

    assert resp.failed == 1
    assert "не найдена" in resp.results[0].reason
