from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class EtranSyncRequest(BaseModel):
    """Входящий запрос от wagon-service для синхронного вызова ЭТРАН."""

    operation: str
    params: dict[str, Any] = {}


class EtranAsyncRequest(BaseModel):
    """Входящий запрос от wagon-service для асинхронного вызова ЭТРАН."""

    operation: str
    params: dict[str, Any] = {}
    callback_url: str | None = None
    priority: Literal["default", "high"] = "default"
