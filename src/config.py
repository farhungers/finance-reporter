"""Environment + timezone constants. Single source of truth for schedule and TZs.

CLAUDE.md §B.4 — timezone constants are LOCKED. Do not modify without operator sign-off.
"""
from __future__ import annotations

import os
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# --- paths ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
KNOWLEDGE_DIR = ROOT / "knowledge"
DB_PATH = DATA_DIR / "finance_reporter.db"
BACKUP_DIR = DATA_DIR / "backups"

load_dotenv(ROOT / ".env")

# --- timezones (LOCKED) --------------------------------------------------
TZ_UTC = ZoneInfo("UTC")
TZ_IST = ZoneInfo("Europe/Istanbul")   # display TZ inside every report body
TZ_ET = ZoneInfo("America/New_York")   # market reference ONLY — never in report text

# --- cron schedule (UTC, LOCKED) -----------------------------------------
# Minute shifted off :00/:30 per §B.4: GitHub Actions defers/drops top-of-hour
# crons under load. GH Actions is now the live scheduler; these constants mirror
# the workflow YAML for the (currently unused) APScheduler path in main.py.
CRON_DAILY_MORNING = "7 3 * * 1-5"     # ~06:07 IST weekdays (shifted 1h earlier 2026-07-30 for drift headroom)
CRON_DAILY_WRAP = "7 13 * * 1-5"       # ~16:07 IST weekdays (shifted 3h earlier 2026-07-30 — pre-US-open outlook)
CRON_WEEKLY_LOOKBACK = "7 13 * * 6"    # ~16:07 IST Sat
CRON_WEEKLY_PREP = "7 13 * * 0"        # ~16:07 IST Sun
CRON_DAILY_BACKUP = "37 3 * * *"       # 03:37 UTC daily — 30 min before morning cron (§E.24)

# --- env-derived flags ---------------------------------------------------
def _bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return default
    return v in {"1", "true", "yes", "on"}


DRY_RUN = _bool("DRY_RUN", True)
KILL_SWITCH_DAILY_MORNING = _bool("KILL_SWITCH_DAILY_MORNING")
KILL_SWITCH_DAILY_WRAP = _bool("KILL_SWITCH_DAILY_WRAP")
KILL_SWITCH_WEEKLY_LOOKBACK = _bool("KILL_SWITCH_WEEKLY_LOOKBACK")
KILL_SWITCH_WEEKLY_PREP = _bool("KILL_SWITCH_WEEKLY_PREP")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").strip().lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "")

# 2026-08-24 roadmap Phase 4.2: opt-in auto-failover to a fallback provider
# on retryable failures (413 request-too-large, 429 rate-limited). Auth
# failures (401) are NEVER auto-failed-over — those must reach the operator
# so the key gets rotated (per Aug 2026 silent-failure incident). Default
# fallback is Cerebras when primary is Groq; empty disables failover.
LLM_AUTO_FAILOVER = _bool("LLM_AUTO_FAILOVER", False)
LLM_FALLBACK_PROVIDER = os.environ.get("LLM_FALLBACK_PROVIDER", "").strip().lower()
if LLM_AUTO_FAILOVER and not LLM_FALLBACK_PROVIDER:
    # Sensible default: cerebras is our built fallback (§Groq-outage 2026-08-18)
    LLM_FALLBACK_PROVIDER = "cerebras" if LLM_PROVIDER == "groq" else ""


KILL_SWITCH_BY_REPORT = {
    "daily_morning": lambda: KILL_SWITCH_DAILY_MORNING,
    "daily_wrap": lambda: KILL_SWITCH_DAILY_WRAP,
    "weekly_lookback": lambda: KILL_SWITCH_WEEKLY_LOOKBACK,
    "weekly_prep": lambda: KILL_SWITCH_WEEKLY_PREP,
}
