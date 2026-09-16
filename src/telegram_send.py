"""Telegram send layer.

Two responsibilities:
  1. esc() — MarkdownV2 escape for every dynamic string (CLAUDE.md §C7, §E.1).
  2. send() — POST to Telegram sendMessage, honoring DRY_RUN.

Every dynamic string interpolated into a report body MUST pass through esc().
Regression test in tests/test_telegram_escape.py.

Token-in-error defense (2026-09-16): the requests library dumps the full URL
into HTTPError messages, which for us includes /bot<TOKEN>/sendMessage. Any
send() failure would leak the bot token to logs / stdout / whatever ate the
exception. All error-path strings now pass through _redact() so the token
never reaches the outside.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

import requests

from src import config

log = logging.getLogger(__name__)

# Telegram MarkdownV2 reserved chars per Bot API docs.
_ESC_CHARS = r"_*[]()~`>#+-=|{}.!\\"
_ESC_TABLE = str.maketrans({c: "\\" + c for c in _ESC_CHARS})

# Bot token format: <digits>:<35+ url-safe chars>. Matches either the standalone
# token or its embedded-in-URL /bot<token>/ form. Captures nothing — the whole
# match is replaced with a fixed sentinel.
_TOKEN_RE = re.compile(r"\d{6,}:[A-Za-z0-9_-]{20,}")


def _redact(s: str) -> str:
    """Strip any bot token from a string. Called on every error-path log
    message and re-raised exception text so a send() failure cannot leak the
    token even if requests / urllib3 embeds it in an HTTPError."""
    if not s:
        return s
    return _TOKEN_RE.sub("<REDACTED_TOKEN>", str(s))


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
    except requests.HTTPError as e:
        # requests embeds the failing URL — which contains the bot token — into
        # HTTPError.__str__. Log the redacted form + Telegram's error body so
        # the operator can still diagnose without the token leaking.
        body = ""
        if e.response is not None:
            try:
                body = e.response.text[:400]
            except Exception:
                pass
        log.error(
            "telegram send failed: status=%s body=%s err=%s",
            e.response.status_code if e.response is not None else "?",
            _redact(body),
            _redact(str(e)),
        )
        return None
    except Exception as e:
        log.error("telegram send failed: %s", _redact(str(e)))
        return None
