"""Unit-тесты для FilterPresetService."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.filter_preset import FilterPresetCreate, FilterPresetUpdate
from app.services.filter_preset_service import FilterPresetService, PRESET_LIMIT_PER_SCOPE


def _make_preset(**kwargs):
    p = MagicMock()
    p.id = kwargs.get("id", uuid.uuid4())
    p.user_id = kwargs.get("user_id", uuid.uuid4())
    p.scope = kwargs.get("scope", "wagon_list")
    p.name = kwargs.get("name", "Мой пресет")
    p.description = kwargs.get("description", None)
    p.filters = kwargs.get("filters", {"status": ["free"]})
    return p


# ---------------------------------------------------------------------------
# Валидация Pydantic-схем
# ---------------------------------------------------------------------------


def test_create_rejects_invalid_scope():
    with pytest.raises(ValueError, match="scope must be one of"):
        FilterPresetCreate(
            scope="invalid_scope",
            name="test",
            filters={"status": ["free"]},
        )


def test_create_rejects_blank_name():
    with pytest.raises(ValueError, match="name must not be blank"):
        FilterPresetCreate(
            scope="wagon_list",
            name="   ",
            filters={"status": ["free"]},
        )


def test_create_rejects_empty_filters():
    with pytest.raises(ValueError, match="filters must not be empty"):
        FilterPresetCreate(
            scope="wagon_list",
            name="test",
            filters={},
        )


def test_create_rejects_filters_with_only_empty_values():
    with pytest.raises(ValueError, match="at least one non-empty value"):
        FilterPresetCreate(
            scope="wagon_list",
            name="test",
            filters={"status": [], "name": ""},
        )


def test_create_strips_name():
    data = FilterPresetCreate(
        scope="wagon_list",
        name="  hello  ",
        filters={"status": ["free"]},
    )
    assert data.name == "hello"


def test_create_valid():
    data = FilterPresetCreate(
        scope="wagon_list",
        name="Мой пресет",
        filters={"status": ["free"]},
    )
    assert data.scope == "wagon_list"


def test_update_allows_partial():
    data = FilterPresetUpdate(name="Новое имя")
    assert data.name == "Новое имя"
    assert data.filters is None


def test_update_rejects_empty_filters():
    with pytest.raises(ValueError, match="filters must not be empty"):
        FilterPresetUpdate(filters={})


# ---------------------------------------------------------------------------
# Сервис: создание пресета
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_preset_success():
    session = AsyncMock()
    service = FilterPresetService(session)

    preset = _make_preset()
    service._repo = AsyncMock()
    service._repo.count_by_user_scope = AsyncMock(return_value=0)
    service._repo.create = AsyncMock(return_value=preset)

    user_id = uuid.uuid4()
    data = FilterPresetCreate(
        scope="wagon_list",
        name="test",
        filters={"status": ["free"]},
    )

    with patch("app.services.filter_preset_service.write_audit_entries", new_callable=AsyncMock):
        result = await service.create(user_id, data)

    assert result == preset
    service._repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_preset_limit_exceeded():
    from fastapi import HTTPException

    session = AsyncMock()
    service = FilterPresetService(session)

    service._repo = AsyncMock()
    service._repo.count_by_user_scope = AsyncMock(return_value=PRESET_LIMIT_PER_SCOPE)

    user_id = uuid.uuid4()
    data = FilterPresetCreate(
        scope="wagon_list",
        name="test",
        filters={"status": ["free"]},
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create(user_id, data)

    assert exc_info.value.status_code == 409


# ---------------------------------------------------------------------------
# Сервис: получение пресета с проверкой владельца
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_one_returns_own_preset():
    session = AsyncMock()
    service = FilterPresetService(session)

    user_id = uuid.uuid4()
    preset = _make_preset(user_id=user_id)
    service._repo = AsyncMock()
    service._repo.get_by_id = AsyncMock(return_value=preset)

    result = await service.get_one(user_id, preset.id)
    assert result == preset


@pytest.mark.asyncio
async def test_get_one_rejects_other_user():
    from fastapi import HTTPException

    session = AsyncMock()
    service = FilterPresetService(session)

    preset = _make_preset(user_id=uuid.uuid4())
    service._repo = AsyncMock()
    service._repo.get_by_id = AsyncMock(return_value=preset)

    other_user = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        await service.get_one(other_user, preset.id)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_one_not_found():
    from fastapi import HTTPException

    session = AsyncMock()
    service = FilterPresetService(session)

    service._repo = AsyncMock()
    service._repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_one(uuid.uuid4(), uuid.uuid4())

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Сервис: удаление пресета
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_preset_success():
    session = AsyncMock()
    service = FilterPresetService(session)

    user_id = uuid.uuid4()
    preset = _make_preset(user_id=user_id)
    service._repo = AsyncMock()
    service._repo.get_by_id = AsyncMock(return_value=preset)
    service._repo.delete_by_id = AsyncMock()

    with patch("app.services.filter_preset_service.write_audit_entries", new_callable=AsyncMock):
        await service.delete(user_id, preset.id)

    service._repo.delete_by_id.assert_awaited_once_with(preset.id)
    session.commit.assert_awaited_once()
