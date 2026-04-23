from __future__ import annotations

import time

import jwt as pyjwt
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app


def _encode(payload: dict) -> str:
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _valid_payload(role: str = "Логист", **overrides) -> dict:
    base = {
        "sub": "user-1",
        "role": role,
        "aud": settings.jwt_audience,
        "exp": int(time.time()) + 3600,
    }
    base.update(overrides)
    return base


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


class TestApiAuthIntegration:
    @pytest.mark.asyncio
    async def test_no_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/wagons")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, client: AsyncClient):
        token = _encode(_valid_payload(exp=int(time.time()) - 10))
        resp = await client.get(
            "/api/v1/wagons",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"]["error_code"] == "TOKEN_EXPIRED"

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/wagons",
            headers={"Authorization": "Bearer garbage"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_role_returns_403(self, client: AsyncClient):
        token = _encode(_valid_payload(role="НеизвестнаяРоль"))
        resp = await client.get(
            "/api/v1/wagons",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
        assert resp.json()["detail"]["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_healthz_no_auth_required(self, client: AsyncClient):
        resp = await client.get("/healthz")
        assert resp.status_code == 200
