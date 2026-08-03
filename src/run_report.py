"""CLI entrypoint for a single report or backup — used by GitHub Actions workflows.

Usage:
    python -m src.run_report daily_morning
    python -m src.run_report daily_wrap
    python -m src.run_report weekly_lookback
    python -m src.run_report weekly_prep
    python -m src.run_report backup

Reads env vars for secrets + DRY_RUN + kill switches (see .env.example).
Persists pitches/trades to SQLite BEFORE any Telegram send (§C10).
Records report_sends row AFTER send attempt.
"""
from __future__ import annotations

import logging
import sys
from typing import Callable

# Defensive: on Windows local runs, stdout defaults to cp1252 which can't encode
# our emoji-rich output. Linux CI (GitHub Actions) is already UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    pass

from src import config, db, knowledge, scheduler, telegram_send
from src.market_data import BLUE_CHIP_UNIVERSE
from src.reports import daily_morning, daily_wrap, weekly_lookback, weekly_prep

log = logging.getLogger(__name__)


REPORTS: dict[str, Callable[[], tuple[str, dict]]] = {
    "daily_morning": daily_morning.generate,
    "daily_wrap": daily_wrap.generate,
    "weekly_lookback": weekly_lookback.generate,
    "weekly_prep": weekly_prep.generate,
}


def _usage() -> None:
    print(
        "usage: python -m src.run_report <report_type>\n"
        "  report_type ∈ {daily_morning, daily_wrap, weekly_lookback, weekly_prep, backup}",
        file=sys.stderr,
    )


def _run_report(report_type: str) -> int:
    """Delegate to scheduler._run_report so the kill-switch + persistence-first
    contract stays in ONE place. Returns 0 on success, non-zero on failure."""
    gen = REPORTS[report_type]
    try:
        scheduler._run_report(report_type, gen)
        return 0
    except Exception as e:
        log.exception("run_report failed: %s", e)
        return 1


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if len(sys.argv) != 2:
        _usage()
        return 2

    kind = sys.argv[1].strip().lower()

    # §E.19 fail-fast: every blue-chip ticker must have its facts file.
    # Skip on backup (no LLM path, no pitches).
    if kind != "backup":
        _present, missing = knowledge.verify_blue_chip_coverage(BLUE_CHIP_UNIVERSE)
        if missing:
            log.error(
                "blue-chip coverage FAIL — missing facts files for %d tickers: %s",
                len(missing), ", ".join(missing),
            )
            return 3

    db.init_db()

    if kind == "backup":
        scheduler._backup_db()
        return 0
    if kind in REPORTS:
        return _run_report(kind)

    _usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
