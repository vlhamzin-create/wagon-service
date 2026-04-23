"""Unit-тесты для API /api/v1/filter-presets."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest import make_token


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token()}"}


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


def _mock_preset(**kwargs):
    p = MagicMock()
    p.id = kwargs.get("id", uuid.uuid4())
    p.user_id = kwargs.get("user_id", uuid.uuid4())
    p.scope = kwargs.get("scope", "wagon_list")
    p.name = kwargs.get("name", "Мой пресет")
    p.description = kwargs.get("description", None)
    p.filters = kwargs.get("filters", {"status": ["free"]})
    p.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    p.updated_at = kwargs.get("updated_at", datetime.now(timezone.utc))
    return p


@pytest.mark.asyncio
async def test_create_preset_401_without_token(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/filter-presets",
        json={"scope": "wagon_list", "name": "test", "filters": {"s": [1]}},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_preset_422_invalid_scope(
    async_client: AsyncClient, auth_headers: dict
):
    resp = await async_client.post(
        "/api/v1/filter-presets",
        json={"scope": "bad", "name": "test", "filters": {"s": [1]}},
        headers=auth_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_preset_success(
    async_client: AsyncClient, auth_headers: dict
):
    preset = _mock_preset()

    with patch(
        "app.api.v1.filter_presets.FilterPresetService"
    ) as mock_cls:
        mock_svc = AsyncMock()
        mock_svc.create = AsyncMock(return_value=preset)
        mock_cls.return_value = mock_svc

        resp = await async_client.post(
            "/api/v1/filter-presets",
            json={
                "scope": "wagon_list",
                "name": "test",
                "filters": {"status": ["free"]},
            },
            headers=auth_headers,
        )

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Мой пресет"
    assert data["scope"] == "wagon_list"


@pytest.mark.asyncio
async def test_list_presets_success(
    async_client: AsyncClient, auth_headers: dict
):
    presets = [_mock_preset(), _mock_preset(name="Second")]

    with patch(
        "app.api.v1.filter_presets.FilterPresetService"
    ) as mock_cls:
        mock_svc = AsyncMock()
        mock_svc.list_by_scope = AsyncMock(return_value=presets)
        mock_cls.return_value = mock_svc

        resp = await async_client.get(
            "/api/v1/filter-presets?scope=wagon_list",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_delete_preset_success(
    async_client: AsyncClient, auth_headers: dict
):
    preset_id = uuid.uuid4()

    with patch(
        "app.api.v1.filter_presets.FilterPresetService"
    ) as mock_cls:
        mock_svc = AsyncMock()
        mock_svc.delete = AsyncMock(return_value=None)
        mock_cls.return_value = mock_svc

        resp = await async_client.delete(
            f"/api/v1/filter-presets/{preset_id}",
            headers=auth_headers,
        )

    assert resp.status_code == 204
