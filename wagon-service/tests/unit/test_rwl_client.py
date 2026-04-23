"""Unit-тесты для RwlClient: пагинация и нормализация."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.rwl_client import RwlClient


def _make_page(items: list[dict], has_more: bool) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"items": items, "has_more": has_more}
    return resp


ITEM_1 = {
    "id": "42",
    "wagon_number": "12345678",
    "owner_type": "собственный",
    "wagon_type": "крытый",
    "model": "11-066",
    "capacity_tons": 68.5,
    "volume_m3": 138.0,
    "current_country": "RU",
    "station_code": "060005",
    "station_name": "Москва-Товарная",
    "city": "Москва",
    "status": "свободен",
}

ITEM_2 = {
    "id": "99",
    "wagon_number": "87654321",
    "owner_type": "арендованный",
    "wagon_type": "полувагон",
    "capacity_tons": 70.0,
}


@pytest.mark.asyncio
async def test_fetch_wagons_single_page():
    client = RwlClient()
    page_resp = _make_page([ITEM_1], has_more=False)

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=page_resp)

    with patch("app.integrations.rwl_client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        wagons = await client.fetch_wagons()

    assert len(wagons) == 1
    w = wagons[0]
    assert w.external_id_rwl == "42"
    assert w.number == "12345678"
    assert w.source == "RWL"
    assert w.capacity_tons == 68.5
    assert w.current_city == "Москва"


@pytest.mark.asyncio
async def test_fetch_wagons_pagination():
    """Проверяем, что клиент обходит несколько страниц."""
    client = RwlClient()
    page1 = _make_page([ITEM_1], has_more=True)
    page2 = _make_page([ITEM_2], has_more=False)

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(side_effect=[page1, page2])

    with patch("app.integrations.rwl_client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        wagons = await client.fetch_wagons()

    assert len(wagons) == 2
    assert mock_http.get.await_count == 2


@pytest.mark.asyncio
async def test_fetch_wagons_empty_items_stops():
    """Пустой items на первой же странице — возвращаем пустой список."""
    client = RwlClient()
    page = _make_page([], has_more=False)

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=page)

    with patch("app.integrations.rwl_client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        wagons = await client.fetch_wagons()

    assert wagons == []


def test_normalize_optional_fields():
    """Нормализация элемента без необязательных полей не падает."""
    client = RwlClient()
    minimal = {"id": "1", "wagon_number": "00000001"}
    wagon = client._normalize(minimal)
    assert wagon.owner_type == "unknown"
    assert wagon.wagon_type == "unknown"
    assert wagon.model is None
    assert wagon.capacity_tons is None
    assert wagon.source == "RWL"
