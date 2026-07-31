"""
Milestone 3 - APScheduler configuration.

Uses BackgroundScheduler (in-process, no Redis/Celery) - an appropriate
level of complexity for this project's scale, consistent with the earlier
decision to skip Celery+Redis for the savings-pool monthly refill.

Called once from main.py's startup event. Job functions live in
backend/scheduler/jobs.py, kept separate from this file so the "what job
does what" logic isn't tangled up with "when does it run" scheduling config.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.scheduler.jobs import (
    check_investment_price_moves,
    send_monthly_summaries,
    check_goal_deadlines,
)

logger = logging.getLogger("finsight.scheduler")

_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> BackgroundScheduler:
    """
    Idempotent - calling this more than once (e.g. if uvicorn --reload fires
    startup twice in dev) just returns the existing scheduler instead of
    registering duplicate jobs.
    """
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # Daily at 08:00 IST - a reasonable time for the day's price-move check
    # to have fresh previous-close data without competing with users' own
    # portfolio-page requests for the shared Alpha Vantage quota during
    # market hours.
    scheduler.add_job(
        check_investment_price_moves,
        trigger=CronTrigger(hour=8, minute=0),
        id="check_investment_price_moves",
        replace_existing=True,
    )

    # Daily at 00:30 IST - catches goals whose status flips purely from the
    # calendar advancing (30-days-remaining threshold), independent of any
    # funding event.
    scheduler.add_job(
        check_goal_deadlines,
        trigger=CronTrigger(hour=0, minute=30),
        id="check_goal_deadlines",
        replace_existing=True,
    )

    # 1st of every month at 06:00 IST - summarizes the month that just ended.
    scheduler.add_job(
        send_monthly_summaries,
        trigger=CronTrigger(day=1, hour=6, minute=0),
        id="send_monthly_summaries",
        replace_existing=True,
    )

    scheduler.start()
    _scheduler = scheduler
    logger.info("APScheduler started with jobs: %s", [j.id for j in scheduler.get_jobs()])
    return scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
