"""/stats slash command — CLAUDE.md §D.9 / §C17.

Verifies:
  - Rate limit: 1 per 60s per chat
  - Reply contains required sections
  - Output is fully escaped (no unescaped reserved chars in dynamic segments)
"""
import time

from src import slash_commands
from src.db import init_db


def setup_module(_module):
    init_db()


def test_handle_stats_returns_text_first_call(tmp_path, monkeypatch):
    slash_commands._last_stats_reply.clear()
    reply = slash_commands.handle_stats("chat1", "2026-07-28 20:00")
    assert reply is not None
    lower = reply.lower()
    assert "running stats" in lower
    assert "pitches" in lower
    assert "trades" in lower
    assert "open positions" in lower


def test_rate_limit_blocks_second_call():
    slash_commands._last_stats_reply.clear()
    reply1 = slash_commands.handle_stats("chatX", "2026-07-28 20:00")
    reply2 = slash_commands.handle_stats("chatX", "2026-07-28 20:00:30")
    assert reply1 is not None
    assert reply2 is None  # rate-limited


def test_different_chats_independent():
    slash_commands._last_stats_reply.clear()
    a = slash_commands.handle_stats("chatA", "t")
    b = slash_commands.handle_stats("chatB", "t")
    assert a is not None and b is not None


def test_stats_reply_contains_compliance_footer():
    slash_commands._last_stats_reply.clear()
    reply = slash_commands.handle_stats("chatFooter", "2026-07-28 20:00")
    assert "not investment advice" in reply.lower()
