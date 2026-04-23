from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_SCOPES = frozenset({"wagon_list"})
CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")


class FilterPresetCreate(BaseModel):
    scope: str = Field(..., max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=512)
    filters: dict[str, Any] = Field(...)

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        if v not in ALLOWED_SCOPES:
            raise ValueError(
                f"scope must be one of: {', '.join(sorted(ALLOWED_SCOPES))}"
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("name must not be blank")
        if CONTROL_CHAR_RE.search(stripped):
            raise ValueError("name must not contain control characters")
        return stripped

    @model_validator(mode="after")
    def validate_filters_not_empty(self) -> FilterPresetCreate:
        if not self.filters:
            raise ValueError("filters must not be empty object")
        has_value = any(
            v not in (None, "", []) for v in self.filters.values()
        )
        if not has_value:
            raise ValueError(
                "filters must contain at least one non-empty value"
            )
        return self


class FilterPresetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=512)
    filters: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("name must not be blank")
        if CONTROL_CHAR_RE.search(stripped):
            raise ValueError("name must not contain control characters")
        return stripped

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: dict | None) -> dict | None:
        if v is None:
            return v
        if not v:
            raise ValueError("filters must not be empty object")
        has_value = any(
            val not in (None, "", []) for val in v.values()
        )
        if not has_value:
            raise ValueError(
                "filters must contain at least one non-empty value"
            )
        return v


class FilterPresetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    scope: str
    name: str
    description: str | None
    filters: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
