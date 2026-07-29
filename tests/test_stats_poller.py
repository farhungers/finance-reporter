"""stats_poller — command detection + update dispatch.

Verifies:
  - /stats regex matches with and without @botname suffix, case-insensitive
  - Non-stats text is skipped
  - Update parsing handles message + channel_post shapes
  - process_updates records every update_id (so offset advances) even for skipped
  - Rate-limited /stats does not fire a send but still records
"""
from __future__ import annotations

import sqlite3
from unittest.mock import patch

import pytest

from src import db, slash_commands, stats_poller


@pytest.fixture(autouse=True)
def _reset(monkeypatch, tmp_path):
    """Point db at a temp file per test and clear the rate-limit cache."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("src.config.DB_PATH", db_path)
    db.init_db()
    slash_commands._last_stats_reply.clear()
    yield


def test_regex_matches_bare_slash_stats():
    assert stats_poller._is_stats_command("/stats")
    assert stats_poller._is_stats_command("/STATS")
    assert stats_poller._is_stats_command("  /stats  ")


def test_regex_matches_with_bot_suffix():
    assert stats_poller._is_stats_command("/stats@TheCapitalOrder_bot")
    assert stats_poller._is_stats_command("/stats@somebot extra ignored")


def test_regex_rejects_non_stats():
    assert not stats_poller._is_stats_command("stats")
    assert not stats_poller._is_stats_command("/statsx")
    assert not stats_poller._is_stats_command("hello /stats world")  # not at start
    assert not stats_poller._is_stats_command("")
    assert not stats_poller._is_stats_command(None)


def test_extract_message_handles_channel_post():
    u = {"update_id": 1, "channel_post": {"chat": {"id": -100}, "text": "/stats"}}
    m = stats_poller._extract_message(u)
    assert m is not None and m["text"] == "/stats"


def test_extract_message_handles_edited():
    u = {"update_id": 1, "edited_message": {"chat": {"id": 42}, "text": "hi"}}
    m = stats_poller._extract_message(u)
    assert m is not None and m["chat"]["id"] == 42


def test_process_updates_records_all_seen_even_non_stats():
    updates = [
        {"update_id": 10, "message": {"chat": {"id": 1}, "text": "hello"}},
        {"update_id": 11, "message": {"chat": {"id": 1}, "text": "/help"}},
    ]
    with patch.object(stats_poller.telegram_send, "send", return_value=None) as mock_send:
        stats_poller.process_updates(updates)
    assert mock_send.call_count == 0
    with db.connect() as conn:
        rows = conn.execute("SELECT update_id, command FROM telegram_updates_seen ORDER BY update_id").fetchall()
    assert [r["update_id"] for r in rows] == [10, 11]
    assert all(r["command"] is None for r in rows)


def test_process_updates_dispatches_stats_and_records_send():
    updates = [
        {"update_id": 20, "message": {"chat": {"id": 999}, "text": "/stats"}},
    ]
    with patch.object(stats_poller.telegram_send, "send", return_value=12345) as mock_send:
        replied = stats_poller.process_updates(updates)
    assert replied == 1
    assert mock_send.call_count == 1
    # send called with chat_id
    args, kwargs = mock_send.call_args
    assert kwargs.get("chat_id") == "999"
    # seen row records command
    with db.connect() as conn:
        row = conn.execute("SELECT command FROM telegram_updates_seen WHERE update_id=20").fetchone()
    assert row["command"] == "/stats"
    # report_sends row logged
    with db.connect() as conn:
        row = conn.execute("SELECT report_type, telegram_message_id FROM report_sends WHERE report_type='stats_reply'").fetchone()
    assert row is not None
    assert row["telegram_message_id"] == 12345


def test_rate_limited_stats_records_but_does_not_send():
    # First /stats call primes the rate limiter
    slash_commands.handle_stats("777", "2026-07-29 12:00")
    updates = [
        {"update_id": 30, "message": {"chat": {"id": 777}, "text": "/stats"}},
    ]
    with patch.object(stats_poller.telegram_send, "send") as mock_send:
        replied = stats_poller.process_updates(updates)
    assert replied == 0
    assert mock_send.call_count == 0
    with db.connect() as conn:
        row = conn.execute("SELECT command FROM telegram_updates_seen WHERE update_id=30").fetchone()
    assert row["command"] == "/stats:rate_limited"


def test_current_offset_advances_past_max_seen():
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO telegram_updates_seen (update_id, seen_at) VALUES (?, ?)",
            (100, "2026-07-29T00:00:00Z"),
        )
        conn.execute(
            "INSERT INTO telegram_updates_seen (update_id, seen_at) VALUES (?, ?)",
            (105, "2026-07-29T00:00:01Z"),
        )
    assert stats_poller._current_offset() == 106


def test_current_offset_zero_when_empty():
    assert stats_poller._current_offset() == 0
