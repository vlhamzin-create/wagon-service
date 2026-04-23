"""Unit-тесты для GET /api/v1/wagons/filters и фильтра client_name в списке вагонов."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.wagon import WagonFiltersResponse
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


MOCK_FILTERS_RESPONSE = WagonFiltersResponse(
    destination_railways=["Октябрьская", "Свердловская"],
    client_names=["Клиент А", "Клиент Б"],
    suppliers=["Поставщик 1"],
    destination_stations=["Москва-Товарная", "Екатеринбург-Сорт"],
)


@pytest.mark.asyncio
async def test_get_filters_returns_client_names(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /wagons/filters возвращает client_names как list[str], а не clients."""
    with patch("app.api.v1.wagons.WagonService") as mock_cls:
        mock_svc = AsyncMock()
        mock_svc.get_filters = AsyncMock(return_value=MOCK_FILTERS_RESPONSE)
        mock_cls.return_value = mock_svc

        resp = await async_client.get(
            "/api/v1/wagons/filters", headers=auth_headers
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "client_names" in data
    assert data["client_names"] == ["Клиент А", "Клиент Б"]
    assert "clients" not in data


@pytest.mark.asyncio
async def test_get_filters_401_without_token(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/wagons/filters")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_filters_response_shape(
    async_client: AsyncClient, auth_headers: dict
):
    """Ответ /filters содержит все четыре массива строк."""
    with patch("app.api.v1.wagons.WagonService") as mock_cls:
        mock_svc = AsyncMock()
        mock_svc.get_filters = AsyncMock(return_value=MOCK_FILTERS_RESPONSE)
        mock_cls.return_value = mock_svc

        resp = await async_client.get(
            "/api/v1/wagons/filters", headers=auth_headers
        )

    data = resp.json()
    assert isinstance(data["destination_railways"], list)
    assert isinstance(data["client_names"], list)
    assert isinstance(data["suppliers"], list)
    assert isinstance(data["destination_stations"], list)


@pytest.mark.asyncio
async def test_list_wagons_accepts_client_name_filter(
    async_client: AsyncClient, auth_headers: dict
):
    """GET /wagons принимает filter[client_name] как repeated query param."""
    with patch("app.api.v1.wagons.WagonService") as mock_cls:
        mock_svc = AsyncMock()
        mock_svc.list_wagons = AsyncMock(
            return_value={
                "items": [],
                "total": 0,
                "limit": 100,
                "offset": 0,
                "has_more": False,
            }
        )
        mock_cls.return_value = mock_svc

        resp = await async_client.get(
            "/api/v1/wagons",
            params=[
                ("filter[client_name]", "Клиент А"),
                ("filter[client_name]", "Клиент Б"),
            ],
            headers=auth_headers,
        )

    assert resp.status_code == 200
    call_args = mock_svc.list_wagons.call_args
    filters = call_args[0][0]
    assert filters.client_name == ["Клиент А", "Клиент Б"]
