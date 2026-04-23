"""Unit-тесты для GET /stations."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest import make_token


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


def _make_station_row(code: str = "060005", name: str = "Москва-Товарная"):
    row = MagicMock()
    row.id = uuid.uuid4()
    row.code = code
    row.name = name
    row.country = "RU"
    row.is_active = True
    return row


@pytest.mark.asyncio
async def test_get_stations_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/stations")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_stations_returns_items(client: AsyncClient):
    headers = {"Authorization": f"Bearer {make_token()}"}
    station = _make_station_row()

    mock_session = AsyncMock()

    # count query
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1

    # data query
    data_scalars = MagicMock()
    data_scalars.all.return_value = [station]
    data_result = MagicMock()
    data_result.scalars.return_value = data_scalars

    mock_session.execute = AsyncMock(side_effect=[count_result, data_result])

    async def _override_db():
        yield mock_session

    app.dependency_overrides[__import__("app.dependencies", fromlist=["get_db"]).get_db] = _override_db

    try:
        resp = await client.get("/api/v1/stations", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1
        assert body["items"][0]["code"] == "060005"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_stations_with_query(client: AsyncClient):
    headers = {"Authorization": f"Bearer {make_token()}"}

    mock_session = AsyncMock()

    count_result = MagicMock()
    count_result.scalar_one.return_value = 0

    data_scalars = MagicMock()
    data_scalars.all.return_value = []
    data_result = MagicMock()
    data_result.scalars.return_value = data_scalars

    mock_session.execute = AsyncMock(side_effect=[count_result, data_result])

    async def _override_db():
        yield mock_session

    from app.dependencies import get_db
    app.dependency_overrides[get_db] = _override_db

    try:
        resp = await client.get("/api/v1/stations?q=Москва&limit=10", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
    finally:
        app.dependency_overrides.clear()
