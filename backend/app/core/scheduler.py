"""APScheduler startup hook — runs the weekly digest job every Sunday 08:00 UTC.

Kept dead simple: one background scheduler tied to the FastAPI lifecycle.
For higher-traffic deployments this should become a separate worker; for a
portfolio project the in-process scheduler is enough.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.db import engine
from app.services.digest import send_weekly_digest
from sqlmodel import Session

log = logging.getLogger("luminary.scheduler")
settings = get_settings()

_scheduler: BackgroundScheduler | None = None


def _run_digest_job() -> None:
    if not settings.DIGEST_ENABLED:
        return
    log.info("weekly digest job starting")
    with Session(engine) as session:
        n = send_weekly_digest(session)
    log.info("weekly digest job finished — %s emails sent", n)


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    if not settings.DIGEST_ENABLED:
        log.info("DIGEST_ENABLED is false; not starting scheduler")
        return
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_digest_job,
        CronTrigger(day_of_week="sun", hour=8, minute=0),
        id="weekly_digest",
        replace_existing=True,
    )
    _scheduler.start()
    log.info("scheduler started; weekly digest cron scheduled")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
