"""Telegram /stats poller — CLAUDE.md §D.9.

Runs on GitHub Actions cron. Fetches updates from Telegram Bot API,
dispatches /stats commands to slash_commands.handle_stats, and sends
replies to the originating chat.

Poll offset is tracked in the telegram_updates_seen table so we don't
reprocess across runs.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any, Optional

import requests

from src import config, db, slash_commands, telegram_send

log = logging.getLogger(__name__)

_STATS_RE = re.compile(r"^/stats(?:@\w+)?(?:\s+.*)?$", re.IGNORECASE)


def _extract_message(update: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Return the message payload from an update, whether direct message or channel post."""
    for k in ("message", "channel_post", "edited_message", "edited_channel_post"):
        m = update.get(k)
        if m:
            return m
    return None


def _is_stats_command(text: Optional[str]) -> bool:
    if not text:
        return False
    return bool(_STATS_RE.match(text.strip()))


def _now_ist_str() -> str:
    return datetime.now(config.TZ_IST).strftime("%Y-%m-%d %H:%M")


def _current_offset() -> int:
    """Next offset for getUpdates = MAX(seen update_id) + 1. Zero on first run."""
    with db.connect() as conn:
        row = conn.execute("SELECT COALESCE(MAX(update_id), -1) AS m FROM telegram_updates_seen").fetchone()
    return (row["m"] + 1) if row and row["m"] is not None else 0


def _record_seen(update_id: int, chat_id: Optional[str], command: Optional[str]) -> None:
    with db.connect() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO telegram_updates_seen (update_id, seen_at, chat_id, command) VALUES (?,?,?,?)",
            (update_id, datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), chat_id, command),
        )


def fetch_updates(offset: int) -> list[dict[str, Any]]:
    """Short-poll Telegram getUpdates. Returns [] on error."""
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        log.error("TELEGRAM_BOT_TOKEN unset — cannot poll")
        return []
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {
        "offset": offset,
        "timeout": 1,
        "allowed_updates": json.dumps(["message", "channel_post"]),
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("result", []) or []
    except Exception as e:
        log.error("getUpdates failed: %s", e)
        return []


def process_updates(updates: list[dict[str, Any]]) -> int:
    """Dispatch /stats commands to slash_commands + send replies.

    Returns number of /stats commands actually replied to (excludes rate-limited)."""
    replied = 0
    for u in updates:
        uid = u.get("update_id")
        if uid is None:
            continue
        msg = _extract_message(u)
        if msg is None:
            _record_seen(int(uid), None, None)
            continue
        chat = msg.get("chat", {}) or {}
        chat_id = str(chat.get("id", "")) if chat.get("id") is not None else None
        text = msg.get("text") or ""
        if not _is_stats_command(text):
            _record_seen(int(uid), chat_id, None)
            continue
        # It's a /stats command — try to reply
        reply = slash_commands.handle_stats(chat_id or "", _now_ist_str())
        if reply is None:
            log.info("update %s: /stats rate-limited for chat %s", uid, chat_id)
            _record_seen(int(uid), chat_id, "/stats:rate_limited")
            continue
        message_id = telegram_send.send(reply, chat_id=chat_id)
        _record_send(chat_id, message_id, len(reply))
        _record_seen(int(uid), chat_id, "/stats")
        replied += 1
        log.info("update %s: /stats replied to chat %s (msg_id=%s)", uid, chat_id, message_id)
    return replied


def _record_send(chat_id: Optional[str], message_id: Optional[int], char_count: int) -> None:
    """Log the reply to report_sends for audit + backup discipline."""
    with db.connect() as conn:
        conn.execute(
            """INSERT INTO report_sends
            (report_type, sent_at, telegram_message_id, char_count, read_minutes_estimate,
             kill_switch_state, dry_run, llm_provider, llm_tokens_in, llm_tokens_out)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                "stats_reply",
                datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                message_id,
                char_count,
                char_count / 1200.0,
                "off",
                1 if config.DRY_RUN else 0,
                None,  # /stats doesn't call the LLM
                0,
                0,
            ),
        )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    db.init_db()
    offset = _current_offset()
    log.info("polling Telegram getUpdates offset=%s", offset)
    updates = fetch_updates(offset)
    log.info("received %d updates", len(updates))
    if not updates:
        return 0
    replied = process_updates(updates)
    log.info("processed %d updates, replied to %d /stats commands", len(updates), replied)
    return 0


if __name__ == "__main__":
    sys.exit(main())
