from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from etran_adapter.config import settings
from etran_adapter.database import AsyncSessionLocal

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session


async def verify_api_key(
    api_key: Annotated[str, Security(_api_key_header)],
) -> str:
    if api_key != settings.internal_api_key.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    return api_key
