"""Unit-тесты для SyncLogRepository.

Все SQL-вызовы замокированы — реальная БД не нужна.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from app.repositories.sync_log_repo import SyncLogRepository


def _make_session() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# upsert_running
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_running_sets_status_running():
    session = _make_session()
    repo = SyncLogRepository(session)

    with patch("app.repositories.sync_log_repo.insert") as mock_insert:
        stmt_mock = MagicMock()
        stmt_mock.values.return_value = stmt_mock
        stmt_mock.on_conflict_do_update.return_value = stmt_mock
        mock_insert.return_value = stmt_mock

        await repo.upsert_running("rwl")

    # values() должен получить last_status='running'
    call_kwargs = stmt_mock.values.call_args[1]
    assert call_kwargs["last_status"] == "running"
    assert call_kwargs["last_success_at"] is None
    assert call_kwargs["last_error"] is None

    session.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# upsert_success
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_success_sets_status_and_success_at():
    session = _make_session()
    repo = SyncLogRepository(session)

    with patch("app.repositories.sync_log_repo.insert") as mock_insert:
        stmt_mock = MagicMock()
        stmt_mock.values.return_value = stmt_mock
        stmt_mock.on_conflict_do_update.return_value = stmt_mock
        mock_insert.return_value = stmt_mock

        await repo.upsert_success("rwl")

    call_kwargs = stmt_mock.values.call_args[1]
    assert call_kwargs["last_status"] == "success"
    assert call_kwargs["last_success_at"] is not None
    assert isinstance(call_kwargs["last_success_at"], datetime)

    # on_conflict set_ должен содержать last_success_at
    set_dict = stmt_mock.on_conflict_do_update.call_args[1]["set_"]
    assert "last_success_at" in set_dict


# ---------------------------------------------------------------------------
# upsert_error
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upsert_error_does_not_update_success_at():
    session = _make_session()
    repo = SyncLogRepository(session)

    with patch("app.repositories.sync_log_repo.insert") as mock_insert:
        stmt_mock = MagicMock()
        stmt_mock.values.return_value = stmt_mock
        stmt_mock.on_conflict_do_update.return_value = stmt_mock
        mock_insert.return_value = stmt_mock

        await repo.upsert_error("onec", "connection refused")

    call_kwargs = stmt_mock.values.call_args[1]
    assert call_kwargs["last_status"] == "error"
    assert call_kwargs["last_error"] == "connection refused"
    # last_success_at НЕ должен появляться в set_
    set_dict = stmt_mock.on_conflict_do_update.call_args[1]["set_"]
    assert "last_success_at" not in set_dict


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_all_returns_list():
    session = _make_session()
    repo = SyncLogRepository(session)

    fake_log = MagicMock()
    fake_log.source = "rwl"

    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [fake_log]
    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars_mock
    session.execute.return_value = execute_result

    result = await repo.get_all()

    assert len(result) == 1
    assert result[0].source == "rwl"
