"""Unit-тесты для OneCClient: fetch_requests и нормализация."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.onec_client import OneCClient


def _make_response(items: list[dict]) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"value": items}
    return resp


REQUEST_ITEM = {
    "Ref_Key": "abc-123",
    "ClientName": "ООО Ромашка",
    "WagonType": "крытый",
    "OriginCode": "060005",
    "DestCode": "812001",
    "PlannedDate": "2024-03-01",
    "Status": "Новая",
}


@pytest.mark.asyncio
async def test_fetch_wagons_returns_empty():
    """1С не является источником вагонов."""
    client = OneCClient()
    wagons = await client.fetch_wagons()
    assert wagons == []


@pytest.mark.asyncio
async def test_fetch_requests_normalizes_correctly():
    client = OneCClient()
    resp_mock = _make_response([REQUEST_ITEM])

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=resp_mock)

    with patch("app.integrations.onec_client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        requests = await client.fetch_requests()

    assert len(requests) == 1
    r = requests[0]
    assert r.external_id_1c == "abc-123"
    assert r.client_name == "ООО Ромашка"
    assert r.required_wagon_type == "крытый"
    assert r.origin_station_code == "060005"
    assert r.destination_station_code == "812001"
    assert r.planned_date == "2024-03-01"
    assert r.status == "Новая"


@pytest.mark.asyncio
async def test_fetch_requests_empty():
    client = OneCClient()
    resp_mock = _make_response([])

    mock_http = AsyncMock()
    mock_http.get = AsyncMock(return_value=resp_mock)

    with patch("app.integrations.onec_client.httpx.AsyncClient") as MockClient:
        MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

        requests = await client.fetch_requests()

    assert requests == []


def test_normalize_request_defaults():
    """Нормализация без необязательных полей не падает."""
    client = OneCClient()
    minimal = {"Ref_Key": "xyz"}
    req = client._normalize_request(minimal)
    assert req.external_id_1c == "xyz"
    assert req.client_name == ""
    assert req.status == "Новая"
