"""Telegram send layer.

Two responsibilities:
  1. esc() — MarkdownV2 escape for every dynamic string (CLAUDE.md §C7, §E.1).
  2. send() — POST to Telegram sendMessage, honoring DRY_RUN.

Every dynamic string interpolated into a report body MUST pass through esc().
Regression test in tests/test_telegram_escape.py.
"""
from __future__ import annotations

import logging
from typing import Optional

import requests

from src import config

log = logging.getLogger(__name__)

# Telegram MarkdownV2 reserved chars per Bot API docs.
_ESC_CHARS = r"_*[]()~`>#+-=|{}.!\\"
_ESC_TABLE = str.maketrans({c: "\\" + c for c in _ESC_CHARS})


def esc(s: str) -> str:
    """Escape a dynamic string for Telegram MarkdownV2. Idempotent-unsafe:
    do not double-escape. Call exactly once per dynamic value at interpolation."""
    if s is None:
        return ""
    return str(s).translate(_ESC_TABLE)


def send(
    text: str,
    chat_id: Optional[str] = None,
    parse_mode: str = "MarkdownV2",
    disable_web_page_preview: bool = True,
) -> Optional[int]:
    """Send a message. Returns telegram_message_id on success, None on failure or DRY_RUN.

    Under DRY_RUN=true, prints to stdout and returns None (caller should still
    persist to DB — persistence-before-send per CLAUDE.md §C10)."""
    if config.DRY_RUN:
        print("=" * 60)
        print("[DRY_RUN send] chat_id=", chat_id or config.TELEGRAM_CHAT_ID)
        print("-" * 60)
        print(text)
        print("=" * 60)
        return None

    token = config.TELEGRAM_BOT_TOKEN
    target_chat = chat_id or config.TELEGRAM_CHAT_ID
    if not token or not target_chat:
        log.error("telegram send skipped: missing token or chat_id")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        result = r.json().get("result", {})
        return result.get("message_id")
    except Exception as e:
        log.error("telegram send failed: %s", e)
        return None
