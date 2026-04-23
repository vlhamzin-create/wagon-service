from __future__ import annotations


class IntegrationError(Exception):
    """Базовый класс для ошибок интеграции."""


class OneCUnavailableError(IntegrationError):
    """1С недоступна (connection timeout, 503)."""


class OneCValidationError(IntegrationError):
    """1С вернула ошибку валидации данных (4xx)."""

    def __init__(self, message: str, response_body: str) -> None:
        super().__init__(message)
        self.response_body = response_body


class OneCServerError(IntegrationError):
    """1С вернула 5xx."""

    def __init__(self, message: str, status_code: int, response_body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class MaxRetriesExceededError(IntegrationError):
    """Исчерпаны все попытки — требуется ручное вмешательство."""
