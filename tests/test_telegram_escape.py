"""MarkdownV2 escape regression — CLAUDE.md §C7 / §E.1.

Every dynamic string interpolated into a Telegram body MUST pass through esc().
This test enforces the character set.
"""
from src.telegram_send import esc


ALL_RESERVED = "_*[]()~`>#+-=|{}.!\\"


def test_all_reserved_chars_escaped():
    for c in ALL_RESERVED:
        result = esc(c)
        assert result == "\\" + c, f"char {c!r} escaped as {result!r}"


def test_mixed_string():
    src = "Hello *world*! [link](url) 3.14 = pi"
    out = esc(src)
    # Every reserved must be backslash-prefixed
    for c in ALL_RESERVED:
        # brute check: count of literal c should equal count of backslash+c
        if c in src:
            assert f"\\{c}" in out, f"{c!r} not escaped in output {out!r}"


def test_none_returns_empty():
    assert esc(None) == ""


def test_plain_ascii_unchanged():
    assert esc("HelloWorld123") == "HelloWorld123"


def test_double_escape_is_safe_to_detect():
    # We do NOT re-escape backslashes we already added, but escaping a raw
    # backslash char in user data adds one. Ensure a bare backslash in input escapes:
    assert "\\\\" in esc("a\\b")


def test_ticker_symbols_survive():
    # BRK-B has a hyphen (reserved). Ensure it escapes properly.
    out = esc("BRK-B")
    assert out == "BRK\\-B"
