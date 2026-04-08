from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

TEST_DB_URL = settings.DATABASE_URL.replace("/medtracker", "/medtracker_test")

test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session():
    async with test_session_factory() as s:
        yield s
        await s.rollback()


class TestRunWithLock:
    @pytest.mark.asyncio
    async def test_acquires_lock_and_runs_job(self, db_session):
        from app.infrastructure.scheduler import _run_with_lock

        job_fn = AsyncMock()

        with patch("app.infrastructure.scheduler.async_session", test_session_factory):
            await _run_with_lock(job_fn, "test_job")

        job_fn.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_when_lock_held(self, db_session):
        from app.infrastructure.scheduler import PUSH_REMINDERS_LOCK_KEY, _run_with_lock

        job_fn = AsyncMock()

        # Hold the advisory lock in a separate session
        async with test_session_factory() as holder_session:
            await holder_session.execute(
                text("SELECT pg_advisory_lock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )

            with patch("app.infrastructure.scheduler.async_session", test_session_factory):
                await _run_with_lock(job_fn, "test_job")

            job_fn.assert_not_awaited()

            await holder_session.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )

    @pytest.mark.asyncio
    async def test_releases_lock_after_job_failure(self, db_session):
        from app.infrastructure.scheduler import PUSH_REMINDERS_LOCK_KEY, _run_with_lock

        job_fn = AsyncMock(side_effect=RuntimeError("boom"))

        with patch("app.infrastructure.scheduler.async_session", test_session_factory):
            await _run_with_lock(job_fn, "test_job")

        # Lock should be released — verify we can acquire it
        async with test_session_factory() as session:
            result = await session.execute(
                text("SELECT pg_try_advisory_lock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )
            assert result.scalar() is True
            await session.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )

    @pytest.mark.asyncio
    async def test_releases_lock_after_timeout(self, db_session):
        import asyncio

        from app.infrastructure.scheduler import PUSH_REMINDERS_LOCK_KEY, _run_with_lock

        async def slow_job():
            await asyncio.sleep(10)

        with (
            patch("app.infrastructure.scheduler.async_session", test_session_factory),
            patch("app.infrastructure.scheduler.settings") as mock_settings,
        ):
            mock_settings.SCHEDULER_LOCK_TIMEOUT = 1
            mock_settings.SCHEDULER_LOCK_KEY = PUSH_REMINDERS_LOCK_KEY
            await _run_with_lock(slow_job, "test_job")

        # Lock should be released after timeout
        async with test_session_factory() as session:
            result = await session.execute(
                text("SELECT pg_try_advisory_lock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )
            assert result.scalar() is True
            await session.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )


class TestSchedulerInit:
    def test_get_sync_database_url(self):
        from app.infrastructure.scheduler import _get_sync_database_url

        sync_url = _get_sync_database_url()
        assert "+psycopg_async" not in sync_url
        assert "+psycopg" in sync_url

    @pytest.mark.asyncio
    async def test_init_and_shutdown(self):
        from app.infrastructure.scheduler import init_scheduler, shutdown_scheduler

        test_sync_url = TEST_DB_URL.replace("+psycopg_async", "+psycopg")

        with patch("app.infrastructure.scheduler._get_sync_database_url", return_value=test_sync_url):
            result = init_scheduler()
            assert result is True

            from app.infrastructure import scheduler
            assert scheduler._scheduler is not None

            shutdown_scheduler()
            assert scheduler._scheduler is None

    def test_init_handles_failure(self):
        from app.infrastructure.scheduler import init_scheduler

        with patch(
            "app.infrastructure.scheduler._get_sync_database_url",
            return_value="postgresql+psycopg://invalid:5432/nonexistent",
        ):
            result = init_scheduler()
            assert result is False


class TestAbstractionBoundary:
    def test_no_scheduler_imports_in_push_scheduler(self):
        import ast
        from pathlib import Path

        source = Path("app/application/push_scheduler.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "apscheduler" not in alias.name.lower()
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "apscheduler" not in node.module.lower()

    def test_no_scheduler_imports_in_main(self):
        import ast
        from pathlib import Path

        source = Path("app/main.py").read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "apscheduler" not in alias.name.lower()
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "apscheduler" not in node.module.lower()
