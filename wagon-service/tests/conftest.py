from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

import jwt

from app.config import settings
from app.main import app


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def make_token(role: str = "Логист", sub: str = "00000000-0000-0000-0000-000000000001") -> str:
    payload = {
        "sub": sub,
        "role": role,
        "aud": settings.jwt_audience,
        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ---------------------------------------------------------------------------
# Фикстуры вагона
# ---------------------------------------------------------------------------

def make_wagon(**kwargs):
    """Создаёт mock-объект вагона с разумными значениями по умолчанию."""
    wagon = MagicMock()
    wagon.id = kwargs.get("id", uuid.uuid4())
    wagon.external_id_rwl = kwargs.get("external_id_rwl", "RWL-001")
    wagon.number = kwargs.get("number", "12345678")
    wagon.owner_type = kwargs.get("owner_type", "собственный")
    wagon.wagon_type = kwargs.get("wagon_type", "крытый")
    wagon.model = kwargs.get("model", None)
    wagon.capacity_tons = kwargs.get("capacity_tons", 60.0)
    wagon.volume_m3 = kwargs.get("volume_m3", 120.0)
    wagon.current_country = kwargs.get("current_country", "RU")
    wagon.current_station_code = kwargs.get("current_station_code", "060005")
    wagon.current_station_name = kwargs.get("current_station_name", "Москва-Товарная")
    wagon.current_city = kwargs.get("current_city", "Москва")
    wagon.destination_station_name = kwargs.get("destination_station_name", None)
    wagon.destination_railway = kwargs.get("destination_railway", None)
    wagon.next_destination_station_code = kwargs.get("next_destination_station_code", None)
    wagon.next_destination_station_name = kwargs.get("next_destination_station_name", None)
    wagon.last_movement_at = kwargs.get("last_movement_at", None)
    wagon.supplier_name = kwargs.get("supplier_name", None)
    wagon.status = kwargs.get("status", "свободен")
    wagon.requires_assignment = kwargs.get("requires_assignment", False)
    wagon.source = kwargs.get("source", "RWL")
    wagon.updated_at = kwargs.get("updated_at", datetime.now(timezone.utc))
    wagon.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
    wagon.deleted_at = kwargs.get("deleted_at", None)
    return wagon


# ---------------------------------------------------------------------------
# HTTP-клиент (async)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token()}"}


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(role='Админ')}"}
