from __future__ import annotations


class AuthError(Exception):
    """Токен отсутствует, невалиден или не прошёл верификацию. -> HTTP 401"""

    def __init__(self, message: str = "Unauthorized", error_code: str = "TOKEN_INVALID"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class TokenExpiredError(AuthError):
    """Токен истёк. -> HTTP 401"""

    def __init__(self, message: str = "Токен истёк"):
        super().__init__(message=message, error_code="TOKEN_EXPIRED")


class ForbiddenError(Exception):
    """Роль пользователя не входит в допустимый список. -> HTTP 403"""

    def __init__(self, message: str = "Forbidden", error_code: str = "FORBIDDEN"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
