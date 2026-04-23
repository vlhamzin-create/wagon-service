from __future__ import annotations

import time
from unittest.mock import AsyncMock

import jwt as pyjwt
import pytest

from fastapi import HTTPException

from app.auth.models import TokenPayload
from app.config import settings
from app.dependencies import get_current_user, require_roles


def _encode(payload: dict) -> str:
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _valid_payload(**overrides) -> dict:
    base = {
        "sub": "user-1",
        "role": "Логист",
        "aud": settings.jwt_audience,
        "exp": int(time.time()) + 3600,
    }
    base.update(overrides)
    return base


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_missing_credentials_returns_401(self):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_valid_token_returns_payload(self):
        token = _encode(_valid_payload())
        creds = AsyncMock()
        creds.credentials = token

        result = await get_current_user(credentials=creds)

        assert isinstance(result, TokenPayload)
        assert result.sub == "user-1"

    @pytest.mark.asyncio
    async def test_expired_token_returns_401_with_error_code(self):
        token = _encode(_valid_payload(exp=int(time.time()) - 10))
        creds = AsyncMock()
        creds.credentials = token

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "TOKEN_EXPIRED"

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self):
        creds = AsyncMock()
        creds.credentials = "garbage"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail["error_code"] == "TOKEN_INVALID"


class TestRequireRoles:
    @pytest.mark.asyncio
    async def test_allowed_role_passes(self):
        payload = TokenPayload(
            sub="u1", exp=int(time.time()) + 3600, aud="wagon-service", role="Логист",
        )
        checker = require_roles("Логист", "Админ")
        result = await checker(token=payload)

        assert result.role == "Логист"

    @pytest.mark.asyncio
    async def test_disallowed_role_raises_403(self):
        payload = TokenPayload(
            sub="u1", exp=int(time.time()) + 3600, aud="wagon-service", role="Просмотр",
        )
        checker = require_roles("Логист", "Админ")

        with pytest.raises(HTTPException) as exc_info:
            await checker(token=payload)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error_code"] == "FORBIDDEN"

    @pytest.mark.asyncio
    async def test_no_roles_arg_uses_all_allowed(self):
        payload = TokenPayload(
            sub="u1", exp=int(time.time()) + 3600, aud="wagon-service", role="Просмотр",
        )
        checker = require_roles()
        result = await checker(token=payload)

        assert result.role == "Просмотр"
