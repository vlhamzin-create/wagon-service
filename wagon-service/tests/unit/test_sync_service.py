"""Unit-тесты для SyncService.run_sync.

Проверяем изоляцию ошибок: сбой одного источника не прерывает другой,
статусы записываются корректно.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.sync_service import SyncService


def _make_service() -> tuple[SyncService, MagicMock]:
    """Создаёт SyncService с замоканным репозиторием."""
    session = AsyncMock()
    service = SyncService(session)

    repo_mock = AsyncMock()
    repo_mock.upsert_running = AsyncMock()
    repo_mock.upsert_success = AsyncMock()
    repo_mock.upsert_error = AsyncMock()
    repo_mock.get_all = AsyncMock(return_value=[])
    service._repo = repo_mock

    return service, repo_mock


# ---------------------------------------------------------------------------
# Успешный запуск обоих источников
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_sync_both_success():
    service, repo = _make_service()

    with (
        patch.object(service, "_sync_rwl", new=AsyncMock()) as mock_rwl,
        patch.object(service, "_sync_onec", new=AsyncMock()) as mock_onec,
    ):
        results = await service.run_sync()

    assert results == {"rwl": "success", "onec": "success"}
    repo.upsert_running.assert_any_await("rwl")
    repo.upsert_running.assert_any_await("onec")
    repo.upsert_success.assert_any_await("rwl")
    repo.upsert_success.assert_any_await("onec")
    repo.upsert_error.assert_not_awaited()


# ---------------------------------------------------------------------------
# RWL падает — 1С всё равно запускается
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_sync_rwl_error_does_not_stop_onec():
    service, repo = _make_service()

    async def _fail():
        raise RuntimeError("connection timeout")

    with (
        patch.object(service, "_sync_rwl", new=AsyncMock(side_effect=_fail)),
        patch.object(service, "_sync_onec", new=AsyncMock()) as mock_onec,
    ):
        results = await service.run_sync()

    assert results["rwl"] == "error"
    assert results["onec"] == "success"

    repo.upsert_error.assert_any_await("rwl", "connection timeout")
    repo.upsert_success.assert_any_await("onec")


# ---------------------------------------------------------------------------
# Оба источника падают
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_sync_both_error():
    service, repo = _make_service()

    async def _fail():
        raise ValueError("boom")

    with (
        patch.object(service, "_sync_rwl", new=AsyncMock(side_effect=_fail)),
        patch.object(service, "_sync_onec", new=AsyncMock(side_effect=_fail)),
    ):
        results = await service.run_sync()

    assert results == {"rwl": "error", "onec": "error"}
    assert repo.upsert_success.await_count == 0
    assert repo.upsert_error.await_count == 2


# ---------------------------------------------------------------------------
# get_status возвращает корректную структуру
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_status_returns_sync_status_response():
    from datetime import datetime, timezone
    from app.schemas.sync_status import SyncStatusResponse

    service, repo = _make_service()

    fake_log = MagicMock()
    fake_log.source = "rwl"
    fake_log.last_success_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    fake_log.last_status = "success"
    fake_log.last_error = None
    repo.get_all = AsyncMock(return_value=[fake_log])

    response = await service.get_status()

    assert isinstance(response, SyncStatusResponse)
    assert len(response.sources) == 1
    assert response.sources[0].source == "rwl"
    assert response.sources[0].last_status == "success"
