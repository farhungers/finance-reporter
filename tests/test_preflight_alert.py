"""Preflight LLM-canary regression — CLAUDE.md §E.24 pattern applied at
run_report entry (2026-08-18 landing commit e299ea1).

Before this guard, a stale/rotated Groq key surfaced only via a swallowed
`generate` exception downstream. Preflight `llm_client.ping()` at run_report
entry converts that into (a) a specific Telegram alert to the operator and
(b) exit code 4 so the GitHub Actions step goes RED. Both are load-bearing —
alone, either one still lets the failure hide.
"""
from __future__ import annotations

from unittest.mock import patch

from src import run_report


def test_preflight_failure_returns_exit_4_and_alerts_operator(monkeypatch):
    sent: list[str] = []

    def fake_send(text: str, **kwargs):
        sent.append(text)
        return 1

    monkeypatch.setattr("sys.argv", ["run_report", "daily_wrap"])
    # Bypass the §E.19 coverage check + DB init — this test is scoped to preflight.
    monkeypatch.setattr(run_report.knowledge, "verify_blue_chip_coverage", lambda _: ([], []))
    monkeypatch.setattr(run_report.db, "init_db", lambda: None)

    with patch("src.llm_client.ping", side_effect=RuntimeError("401 Invalid API Key")), \
         patch("src.telegram_send.send", side_effect=fake_send), \
         patch("src.telegram_send.esc", side_effect=lambda s: s):
        rc = run_report.main()

    assert rc == 4, "preflight failure must return exit 4 so GH step goes RED"
    assert sent, "operator Telegram alert was not sent"
    body = sent[0]
    assert "daily_wrap" in body and "LLM key invalid" in body


def test_preflight_alert_send_failure_does_not_mask_exit_code(monkeypatch):
    """Telegram down at the moment of alert must not swallow the exit code."""
    monkeypatch.setattr("sys.argv", ["run_report", "daily_wrap"])
    monkeypatch.setattr(run_report.knowledge, "verify_blue_chip_coverage", lambda _: ([], []))
    monkeypatch.setattr(run_report.db, "init_db", lambda: None)

    def broken_send(text: str, **kwargs):
        raise RuntimeError("telegram down")

    with patch("src.llm_client.ping", side_effect=RuntimeError("401")), \
         patch("src.telegram_send.send", side_effect=broken_send), \
         patch("src.telegram_send.esc", side_effect=lambda s: s):
        rc = run_report.main()

    assert rc == 4, "exit code must still be 4 even when alert delivery fails"


def test_preflight_skipped_for_weekly_lookback(monkeypatch):
    """weekly_lookback renders from DB rows only — no LLM call, so no preflight.
    A bad Groq key must not block Saturday's calibration report."""
    monkeypatch.setattr("sys.argv", ["run_report", "weekly_lookback"])
    monkeypatch.setattr(run_report.knowledge, "verify_blue_chip_coverage", lambda _: ([], []))
    monkeypatch.setattr(run_report.db, "init_db", lambda: None)

    ping_called = []

    def spy_ping():
        ping_called.append(True)

    with patch("src.llm_client.ping", side_effect=spy_ping), \
         patch("src.run_report._run_report", return_value=0):
        rc = run_report.main()

    assert rc == 0
    assert ping_called == [], "weekly_lookback must not call the LLM preflight"
