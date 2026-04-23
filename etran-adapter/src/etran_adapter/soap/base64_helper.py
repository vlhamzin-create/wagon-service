from __future__ import annotations

import base64
import re

_BASE64_RE = re.compile(r"^[A-Za-z0-9+/\n\r]+=*$")


def encode_text(text: str) -> str:
    """Кодирует строку в base64 (UTF-8)."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def decode_text(b64_string: str) -> str:
    """Декодирует base64-строку в UTF-8 текст."""
    return base64.b64decode(b64_string).decode("utf-8")


def is_base64(value: str) -> bool:
    """Эвристическая проверка, является ли строка base64-кодированной.

    Проверяет символьный состав и кратность длины 4.
    """
    stripped = value.strip()
    if not stripped or len(stripped) % 4 != 0:
        return False
    return bool(_BASE64_RE.match(stripped))
