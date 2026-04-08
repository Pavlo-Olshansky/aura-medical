from __future__ import annotations

import asyncio

import structlog
from sqlalchemy import text

from app.config import settings
from app.infrastructure.database import async_session

logger = structlog.get_logger()

_scheduler = None

PUSH_REMINDERS_LOCK_KEY = settings.SCHEDULER_LOCK_KEY


def _get_sync_database_url() -> str:
    return settings.DATABASE_URL.replace("+psycopg_async", "+psycopg")


async def _run_with_lock(job_fn, job_name: str) -> None:
    async with async_session() as session:
        result = await session.execute(
            text("SELECT pg_try_advisory_lock(:key)"),
            {"key": PUSH_REMINDERS_LOCK_KEY},
        )
        acquired = result.scalar()

        if not acquired:
            logger.info("job_lock_skipped", job=job_name, reason="already_locked")
            return

        logger.info("job_lock_acquired", job=job_name)
        try:
            async with asyncio.timeout(settings.SCHEDULER_LOCK_TIMEOUT):
                await job_fn()
            logger.info("job_executed", job=job_name)
        except TimeoutError:
            logger.error("job_timeout", job=job_name, timeout=settings.SCHEDULER_LOCK_TIMEOUT)
        except Exception:
            logger.exception("job_failed", job=job_name)
        finally:
            await session.execute(
                text("SELECT pg_advisory_unlock(:key)"),
                {"key": PUSH_REMINDERS_LOCK_KEY},
            )


def _on_job_event(event) -> None:
    from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

    if event.code == EVENT_JOB_MISSED:
        logger.warning("job_misfired", job_id=event.job_id)
    elif event.code == EVENT_JOB_ERROR:
        logger.error("job_error_event", job_id=event.job_id, exception=str(event.exception))


def init_scheduler() -> bool:
    global _scheduler
    try:
        from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        jobstores = {"default": SQLAlchemyJobStore(url=_get_sync_database_url())}
        _scheduler = AsyncIOScheduler(jobstores=jobstores)
        _scheduler.add_listener(_on_job_event, EVENT_JOB_ERROR | EVENT_JOB_MISSED)

        register_jobs()

        _scheduler.start()
        logger.info("scheduler_started", jobstore="postgresql")
        return True
    except Exception:
        logger.exception("scheduler_init_failed")
        _scheduler = None
        return False


def register_jobs() -> None:
    from app.application.push_scheduler import send_push_reminders

    async def locked_push_reminders():
        await _run_with_lock(send_push_reminders, "push_reminders")

    _scheduler.add_job(
        locked_push_reminders,
        "interval",
        minutes=15,
        id="push_reminders",
        replace_existing=True,
        misfire_grace_time=900,
        coalesce=True,
    )


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped")
        _scheduler = None
