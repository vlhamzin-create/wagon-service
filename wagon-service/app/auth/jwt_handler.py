from __future__ import annotations

from dataclasses import dataclass, field

import jwt
from jwt import PyJWTError

from app.config import settings


@dataclass
class CurrentUser:
    sub: str
    roles: list[str] = field(default_factory=list)
    username: str = ""


def decode_token(token: str) -> CurrentUser:
    """Декодирует JWT и возвращает CurrentUser.

    Поднимает jwt.PyJWTError при невалидном/просроченном токене.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
    )
    sub: str = payload.get("sub", "")
    roles: list[str] = payload.get("roles", [])
    username: str = payload.get("username", sub)
    return CurrentUser(sub=sub, roles=roles, username=username)
