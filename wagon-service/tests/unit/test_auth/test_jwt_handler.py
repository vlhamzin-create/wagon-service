from __future__ import annotations

import time

import jwt as pyjwt
import pytest

from app.auth.exceptions import AuthError, TokenExpiredError
from app.auth.jwt_handler import decode_token
from app.auth.models import TokenPayload
from app.config import settings


def _encode(payload: dict, secret: str | None = None, algorithm: str | None = None) -> str:
    return pyjwt.encode(
        payload,
        secret or settings.jwt_secret,
        algorithm=algorithm or settings.jwt_algorithm,
    )


def _valid_payload(**overrides) -> dict:
    base = {
        "sub": "user-1",
        "role": "Логист",
        "aud": settings.jwt_audience,
        "exp": int(time.time()) + 3600,
    }
    base.update(overrides)
    return base


class TestDecodeTokenSuccess:
    def test_valid_token_returns_token_payload(self):
        token = _encode(_valid_payload())
        result = decode_token(token)

        assert isinstance(result, TokenPayload)
        assert result.sub == "user-1"
        assert result.role == "Логист"

    def test_role_list_normalized_to_first_element(self):
        token = _encode(_valid_payload(role=["Админ", "Логист"]))
        result = decode_token(token)

        assert result.role == "Админ"

    def test_extra_claims_ignored(self):
        token = _encode(_valid_payload(custom_field="value"))
        result = decode_token(token)

        assert result.sub == "user-1"
        assert not hasattr(result, "custom_field")


class TestDecodeTokenExpired:
    def test_expired_token_raises_token_expired_error(self):
        token = _encode(_valid_payload(exp=int(time.time()) - 10))

        with pytest.raises(TokenExpiredError) as exc_info:
            decode_token(token)

        assert exc_info.value.error_code == "TOKEN_EXPIRED"


class TestDecodeTokenInvalid:
    def test_bad_signature_raises_auth_error(self):
        token = _encode(_valid_payload(), secret="wrong-secret")

        with pytest.raises(AuthError) as exc_info:
            decode_token(token)

        assert exc_info.value.error_code == "TOKEN_INVALID"

    def test_wrong_audience_raises_auth_error(self):
        token = _encode(_valid_payload(aud="other-service"))

        with pytest.raises(AuthError):
            decode_token(token)

    def test_malformed_token_raises_auth_error(self):
        with pytest.raises(AuthError):
            decode_token("not-a-jwt")

    def test_missing_sub_raises_auth_error(self):
        payload = _valid_payload()
        del payload["sub"]
        token = _encode(payload)

        with pytest.raises(AuthError):
            decode_token(token)
