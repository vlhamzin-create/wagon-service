"""Unit-тесты для GET /clients."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

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


def _make_client_row(name: str = "ООО Ромашка"):
    row = MagicMock()
    row.id = uuid.uuid4()
    row.name = name
    row.external_id_1c = "1C-001"
    row.is_active = True
    return row


@pytest.mark.asyncio
async def test_get_clients_unauthorized(client: AsyncClient):
    resp = await client.get("/api/v1/clients")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_clients_returns_items(client: AsyncClient):
    headers = {"Authorization": f"Bearer {make_token()}"}
    cl = _make_client_row()

    mock_session = AsyncMock()

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1

    data_scalars = MagicMock()
    data_scalars.all.return_value = [cl]
    data_result = MagicMock()
    data_result.scalars.return_value = data_scalars

    mock_session.execute = AsyncMock(side_effect=[count_result, data_result])

    from app.dependencies import get_db

    async def _override_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_db

    try:
        resp = await client.get("/api/v1/clients", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1
        assert body["items"][0]["name"] == "ООО Ромашка"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_clients_with_query(client: AsyncClient):
    headers = {"Authorization": f"Bearer {make_token()}"}

    mock_session = AsyncMock()

    count_result = MagicMock()
    count_result.scalar_one.return_value = 0

    data_scalars = MagicMock()
    data_scalars.all.return_value = []
    data_result = MagicMock()
    data_result.scalars.return_value = data_scalars

    mock_session.execute = AsyncMock(side_effect=[count_result, data_result])

    from app.dependencies import get_db

    async def _override_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_db

    try:
        resp = await client.get("/api/v1/clients?q=Ромашка&limit=5", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
    finally:
        app.dependency_overrides.clear()
