"""APScheduler wrapper — 4 report crons + daily backup (CLAUDE.md §B.4, §E.24).

Each report path respects (a) its kill switch and (b) global DRY_RUN.
Persistence-before-send: pitches/trades written inside the generate() modules;
this layer records the report_sends row + calls telegram_send after.
"""
from __future__ import annotations

import logging
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from src import config, db, telegram_send
from src.reports import daily_morning, daily_wrap, weekly_lookback, weekly_prep

log = logging.getLogger(__name__)


def _record_send(report_type: str, text: str, message_id: int | None, telemetry: dict, kill: bool) -> None:
    read_min = len(text) / 1200.0  # crude: ~1200 chars/min at telegram scan speed
    with db.connect() as conn:
        conn.execute(
            """INSERT INTO report_sends
            (report_type, sent_at, telegram_message_id, char_count, read_minutes_estimate,
             kill_switch_state, dry_run, llm_provider, llm_tokens_in, llm_tokens_out)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                report_type,
                datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                message_id,
                len(text),
                read_min,
                "on" if kill else "off",
                1 if config.DRY_RUN else 0,
                config.LLM_PROVIDER,
                telemetry.get("llm_tokens_in", 0),
                telemetry.get("llm_tokens_out", 0),
            ),
        )


def _run_report(report_type: str, gen_fn: Callable[[], tuple[str, dict]]) -> None:
    kill = config.KILL_SWITCH_BY_REPORT.get(report_type, lambda: False)()
    if kill:
        log.warning("kill switch ON for %s — skipping generate + send", report_type)
        _record_send(report_type, "(killed)", None, {}, kill=True)
        return
    try:
        text, telemetry = gen_fn()
    except Exception as e:
        log.exception("report %s generation failed: %s", report_type, e)
        return
    message_id = telegram_send.send(text)
    _record_send(report_type, text, message_id, telemetry, kill=False)


def _backup_db() -> None:
    src_p = Path(str(config.DB_PATH))
    if not src_p.exists():
        return
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    dst = config.BACKUP_DIR / f"{ts}_finance_reporter.db"
    config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        # Use SQLite backup API (safe with active connections)
        with sqlite3.connect(str(src_p)) as src_conn, sqlite3.connect(str(dst)) as dst_conn:
            src_conn.backup(dst_conn)
        _prune_backups(retention_days=30)
    except Exception as e:
        log.error("SQLITE BACKUP FAILED (LOUD per §E.24): %s", e)
        try:
            telegram_send.send(
                telegram_send.esc(f"⚠ SQLite backup failed at {ts}: {e}")
            )
        except Exception:
            pass


def _prune_backups(retention_days: int = 30) -> None:
    if not config.BACKUP_DIR.exists():
        return
    cutoff = datetime.now(UTC).timestamp() - retention_days * 86400
    for f in config.BACKUP_DIR.glob("*_finance_reporter.db"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except Exception as e:
            log.warning("prune backup failed for %s: %s", f, e)


def build_scheduler() -> BlockingScheduler:
    sched = BlockingScheduler(timezone="UTC")

    sched.add_job(
        lambda: _run_report("daily_morning", daily_morning.generate),
        CronTrigger.from_crontab(config.CRON_DAILY_MORNING, timezone="UTC"),
        id="daily_morning",
    )
    sched.add_job(
        lambda: _run_report("daily_wrap", daily_wrap.generate),
        CronTrigger.from_crontab(config.CRON_DAILY_WRAP, timezone="UTC"),
        id="daily_wrap",
    )
    sched.add_job(
        lambda: _run_report("weekly_lookback", weekly_lookback.generate),
        CronTrigger.from_crontab(config.CRON_WEEKLY_LOOKBACK, timezone="UTC"),
        id="weekly_lookback",
    )
    sched.add_job(
        lambda: _run_report("weekly_prep", weekly_prep.generate),
        CronTrigger.from_crontab(config.CRON_WEEKLY_PREP, timezone="UTC"),
        id="weekly_prep",
    )
    sched.add_job(
        _backup_db,
        CronTrigger.from_crontab(config.CRON_DAILY_BACKUP, timezone="UTC"),
        id="daily_backup",
    )
    return sched
