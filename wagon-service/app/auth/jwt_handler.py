from __future__ import annotations

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidTokenError,
)

from app.auth.exceptions import AuthError, TokenExpiredError
from app.auth.models import TokenPayload
from app.config import settings


def decode_token(token: str) -> TokenPayload:
    """Декодирует и верифицирует JWT access-токен.

    Выбрасывает:
      TokenExpiredError  — если exp истёк
      AuthError          — если подпись невалидна, токен malformed,
                           аудитория не совпадает
    """
    try:
        payload: dict = jwt.decode(
            token,
            key=settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            options={
                "require": ["sub", "exp", "aud"],
            },
        )
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Токен истёк") from exc
    except InvalidAudienceError as exc:
        raise AuthError("Неверная аудитория токена") from exc
    except InvalidTokenError as exc:
        raise AuthError(f"Невалидный токен: {exc}") from exc

    return TokenPayload.model_validate(payload)
