"""/health command regression — 2026-08-18 defense against silent-failure blind spot.

Prior behavior: LLM 401 for 4 straight days (2026-08-14 → 2026-08-18) went
undetected because there was no operator-facing freshness surface. /health now
shows last-send per report_type + a red/green flag when age exceeds threshold.
"""
from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from src import accuracy, db, slash_commands, stats_poller


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    p = tmp_path / "test.db"
    monkeypatch.setattr("src.config.DB_PATH", p)
    db.init_db(p)
    yield p


def _insert_send(conn: sqlite3.Connection, report_type: str, sent_at_utc: datetime, msg_id: int = 1):
    conn.execute(
        """INSERT INTO report_sends
        (report_type, sent_at, telegram_message_id, char_count, read_minutes_estimate,
         kill_switch_state, dry_run, llm_provider, llm_tokens_in, llm_tokens_out)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (report_type, sent_at_utc.strftime("%Y-%m-%dT%H:%M:%SZ"), msg_id, 100, 0.1, "off", 0, "groq", 0, 0),
    )


def test_last_send_by_type_flags_stale(tmp_db):
    now = datetime.now(UTC)
    with db.connect(tmp_db) as conn:
        _insert_send(conn, "daily_morning", now - timedelta(hours=48))     # STALE
        _insert_send(conn, "daily_wrap", now - timedelta(hours=2))          # OK
        _insert_send(conn, "weekly_lookback", now - timedelta(days=3))     # OK
        # weekly_prep never sent → also STALE

    fresh = accuracy.last_send_by_type()
    assert fresh["daily_morning"]["stale"] is True
    assert fresh["daily_wrap"]["stale"] is False
    assert fresh["weekly_lookback"]["stale"] is False
    assert fresh["weekly_prep"]["stale"] is True
    assert fresh["weekly_prep"]["last_sent_utc"] is None


def test_render_health_includes_all_four_types(tmp_db):
    with db.connect(tmp_db) as conn:
        _insert_send(conn, "daily_morning", datetime.now(UTC) - timedelta(hours=1))
    body = slash_commands.render_health("2026-08-18 23:57")
    # Report names live inside a MarkdownV2 code_block, so they're NOT escaped.
    for rt in ("daily_morning", "daily_wrap", "weekly_lookback", "weekly_prep"):
        assert rt in body
    assert "HEALTH" in body
    assert "STALE" in body or "OK" in body


def test_health_regex_matches():
    assert stats_poller._is_health_command("/health")
    assert stats_poller._is_health_command("/HEALTH")
    assert stats_poller._is_health_command("/health@finance_bot")
    assert not stats_poller._is_health_command("/stats")
    assert not stats_poller._is_health_command("health")


def test_handle_health_rate_limited_on_second_call(tmp_db):
    # First call passes
    r1 = slash_commands.handle_health("chat-A", "2026-08-18 23:00")
    assert r1 is not None
    # Second call within 60s returns None
    r2 = slash_commands.handle_health("chat-A", "2026-08-18 23:00:30")
    assert r2 is None
    # Different chat is not rate-limited
    r3 = slash_commands.handle_health("chat-B", "2026-08-18 23:00:30")
    assert r3 is not None
