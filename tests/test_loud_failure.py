"""LOUD-failure regression — CLAUDE.md §E.24 pattern applied to LLM path.

Prior behavior: scheduler._run_report swallowed generation exceptions, returned
None, and let the workflow step exit 0. Four consecutive days of missed reports
(2026-08-14 → 2026-08-18) went undetected because of this. Guard: re-raise so
the workflow step fails, and best-effort Telegram alert to the operator.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src import scheduler


def test_generation_failure_reraises_and_alerts():
    sent: list[str] = []

    def fake_send(text: str, **kwargs):
        sent.append(text)
        return 1

    def bad_gen():
        raise RuntimeError("groq failed after retries: 401 Invalid API Key")

    with patch("src.telegram_send.send", side_effect=fake_send), \
         patch("src.config.KILL_SWITCH_BY_REPORT", {"daily_morning": lambda: False}):
        with pytest.raises(RuntimeError, match="401 Invalid API Key"):
            scheduler._run_report("daily_morning", bad_gen)

    assert sent, "operator alert Telegram send was not called"
    body = sent[0]
    # Underscores are escaped for MarkdownV2 per §C7/§E.1.
    assert "daily\\_morning" in body
    assert "FAILED" in body
    assert "RuntimeError" in body


def test_generation_success_does_not_alert():
    sent: list[str] = []

    def fake_send(text: str, **kwargs):
        sent.append(text)
        return 42

    def good_gen():
        return ("hello", {"tokens_in": 10, "tokens_out": 5})

    with patch("src.telegram_send.send", side_effect=fake_send), \
         patch("src.config.KILL_SWITCH_BY_REPORT", {"daily_morning": lambda: False}), \
         patch("src.scheduler._record_send") as rec:
        scheduler._run_report("daily_morning", good_gen)

    # Only the report body was sent — no alert.
    assert sent == ["hello"]
    rec.assert_called_once()


def test_alert_send_failure_does_not_mask_original():
    def bad_gen():
        raise ValueError("original problem")

    def broken_send(text: str, **kwargs):
        raise RuntimeError("telegram down")

    with patch("src.telegram_send.send", side_effect=broken_send), \
         patch("src.config.KILL_SWITCH_BY_REPORT", {"daily_morning": lambda: False}):
        with pytest.raises(ValueError, match="original problem"):
            scheduler._run_report("daily_morning", bad_gen)
