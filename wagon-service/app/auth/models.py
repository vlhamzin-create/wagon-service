from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

ROLE_CLAIM_NAME = "role"


class TokenPayload(BaseModel):
    """Валидированный payload JWT access-токена.

    Обязательные стандартные claims (RFC 7519):
      - sub: идентификатор пользователя
      - exp: время истечения (проверяется PyJWT автоматически до парсинга)
      - aud: аудитория (проверяется PyJWT при decode)

    Кастомные claims:
      - role: роль пользователя
    """

    sub: str
    exp: int
    aud: str | list[str]
    role: str = Field(alias=ROLE_CLAIM_NAME)

    model_config = {"extra": "ignore", "populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def normalize_role_claim(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Нормализует claim роли: если приходит список — берём первый элемент."""
        raw = data.get(ROLE_CLAIM_NAME)
        if isinstance(raw, list):
            data[ROLE_CLAIM_NAME] = raw[0] if raw else ""
        return data
