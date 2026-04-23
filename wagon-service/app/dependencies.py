from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.exceptions import AuthError, TokenExpiredError
from app.auth.jwt_handler import decode_token
from app.auth.models import TokenPayload
from app.config import settings
from app.database import AsyncSessionLocal

_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> TokenPayload:
    """Извлекает и верифицирует JWT токен из заголовка Authorization."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "UNAUTHORIZED", "message": "Требуется аутентификация"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return decode_token(credentials.credentials)
    except TokenExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": exc.error_code, "message": exc.message},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": exc.error_code, "message": exc.message},
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_roles(*roles: str):
    """Фабрика зависимостей: проверяет, что роль пользователя входит в допустимый список.

    Если roles не переданы — используется settings.allowed_roles.
    """
    _allowed = roles or tuple(settings.allowed_roles)

    async def _check(
        token: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if token.role not in _allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "FORBIDDEN",
                    "message": f"Роль '{token.role}' не имеет доступа к ресурсу",
                },
            )
        return token

    return _check


# Предустановленная зависимость для всех эндпоинтов — любая разрешённая роль
require_any_role = require_roles(*settings.allowed_roles)
